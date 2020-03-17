"""
This is abstract class for ion mass-analyzer traps.
It creates needed PA file, and works with it
:auther: Anton Lioznov anton.lioznov@skoltech.ru
"""

import os
import subprocess
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import typing
import numpy as np
from math import ceil
from tqdm import tqdm_notebook as tqdm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .voltage_enums import Voltages
from SIMION.PA import PA
from enum import Enum, auto
T = typing.TypeVar('T')
AVERAGED_AREA_LENGTH = 10 * 10 ** -3


@dataclass
class Coords(typing.Generic[T]):
    """dataclass for 3D coord"""
    x: T
    y: T
    z: T


CoordsVar = typing.Tuple[float, float, float]  # (x, y, z) or (r, theta, z)
SIMION_LOCATION = os.path.abspath("SIMION-8.1/simion.exe")
NO_GUI_STR = "--nogui"
REFINE_STR = "refine"
ADJUST_STR = "fastadj"



class AbstractTrap(metaclass=ABCMeta):
    """
    The most common class for creating a trap with SIMION interaction
    """

    name = "abstract"  # the name of the trap (for file naming)
    _voltages = Voltages  # the voltages enum for creating fast-adjust after refining

    def _create_geometry(
            self, trap_border: Coords[float],
            *, pts=150, model_border: typing.Optional[Coords[float]] =None,
            cylindrical_geometry=False
    ):
        """
        creates all geometry needed params and grids. We use xyz-mirrowing for it
        :param trap_border: the 3 coords of characteristic x, y, z border of the trap
          (it is either the described cuboid lengths or the naturally appeared from equation)
        :param pts: the number of points per grid in x-direction
        :param model_border: the 3 coords describe the model border (if not given use default - cell_coords*1.5)
        :param cylindrical_geometry: is this trap using cylindrical geometry in equations
        :return:
        """
        # the first thing to do: determine the exact parameters of the model.
        # by default they are slightly (1.5 times) larger than the size of the trap
        # after that you need to slightly correct them so that an integer number of grid steps fit into the size
        bigger = 1.5
        model_border = model_border if model_border else Coords[float](
            x=bigger * trap_border.x,
            y=bigger * trap_border.y,
            z=bigger * trap_border.z
        )
        self.pts = pts
        gridstepmm = model_border.x / pts
        # Now we slightly adjust all the coordinates so that the integer number of `gridstepmm` fits into them
        self.model_lenghts = Coords[int](
            x=ceil(model_border.x/gridstepmm),
            y=ceil(model_border.y/gridstepmm),
            z=ceil(model_border.z/gridstepmm)
        )
        model_border = Coords(
            x=self.model_lenghts.x * gridstepmm,
            y=self.model_lenghts.y * gridstepmm,
            z=self.model_lenghts.z * gridstepmm
        )
        self.trap_border = trap_border
        self.model_border = model_border
        self.gridstepmm = gridstepmm
        self.grid = Coords[np.ndarray](
            x=np.linspace(0, self.model_border.x, self.model_lenghts.x),
            y=np.linspace(0, self.model_border.y, self.model_lenghts.y),
            z=np.linspace(0, self.model_border.z, self.model_lenghts.z)
        )
        self.avar_grid = (
            np.linspace(0, self.model_border.x, self.model_lenghts.x),
            np.linspace(0, self.model_border.z, self.model_lenghts.z)
        )
        self.thetas = None
        self.rs = None
        if cylindrical_geometry:
            self.thetas = np.empty((self.model_lenghts.x, self.model_lenghts.y))
            self.rs = np.empty((self.model_lenghts.x, self.model_lenghts.y))
            for j in range(self.model_lenghts.y):
                for i in range(self.model_lenghts.x):
                    self.thetas[j, i] = np.arctan2(self.grid.y[j], self.grid.x[i])
                    self.rs[j, i] = np.sqrt(self.grid.y[j]**2 + self.grid.x[i]**2)

    def get_d(self, r0=None, z0=None):
        """The characteristic size of trap"""
        r0 = r0 if r0 else self.trap_border.x
        z0 = z0 if z0 else self.trap_border.z
        return np.sqrt(1 / 2 * (z0 ** 2 + 1 / 2 * r0 ** 2))

    def create_dump_pa(self) -> PA:
        """
        Creates empty PA file using the geometry params, that was calculated
        :return:
        """
        return PA(
            symmetry='planar',  # symmetry type: 'planar' or 'cylindrical'
            max_voltage=100000,  # this affects the interpretation
            #   of point values
            nx=self.model_lenghts.x,  # x dimension in grid units
            ny=self.model_lenghts.y,  # y dimension in grid units
            nz=self.model_lenghts.z,  # z dimension in grid units
            mirror='xyz',  # mirroring (subset of "xyz")
            field_type='electrostatic',  # field type: 'electrostatic' or 'magnetic'
            ng=100,  # ng scaling factor for magnetic arrays.
            # The following three fields are only supported in SIMION 8.1
            dx_mm=self.gridstepmm,  # grid unit size (mm) in X direction
            dy_mm=self.gridstepmm,  # grid unit size (mm) in Y direction
            dz_mm=self.gridstepmm,  # grid unit size (mm) in Z direction
            fast_adjustable=0,  # Boolean indicating whether is fast-adj.
            enable_points=1  # Enable data points.
        )

    def __init__(
            self, trap_border: Coords[float], pa_file_name="test", *,
            pts=150, model_border: typing.Optional[Coords[float]] =None,
            cylindrical_geometry=False
    ):
        assert os.path.exists(SIMION_LOCATION), f"You need to use SIMION for refine trap. Put it in {SIMION_LOCATION}"
        self.pa_filename = pa_file_name
        self.cylindrical_geometry = cylindrical_geometry
        self._create_geometry(trap_border,
                              pts=pts, model_border=model_border, cylindrical_geometry=cylindrical_geometry)
        self.unrefined_pa = self.create_dump_pa()
        self.pa = self.unrefined_pa

    @abstractmethod
    def is_electrode(self, coords: CoordsVar):
        """is the point in the electrode"""
        pass

    @abstractmethod
    def get_electrode_type(self, coords: CoordsVar) -> int:
        """what type is the electrode"""
        pass

    def put_point(self, indexes, coords):
        """put a point to pa file"""
        i, j, k = indexes
        if self.is_electrode(coords):
            self.unrefined_pa.point(i, j, k, 1, self.get_electrode_type(coords))

    def _go_throw_volume(self, func: typing.Callable[[typing.Tuple[int, int, int], CoordsVar], typing.Any],
                         always_cartesian=False):
        """go throw whole volume of the model and apply a `func`"""
        res = []
        for k, z in tqdm(enumerate(self.grid.z), total=self.model_lenghts.z):
            for i, x in enumerate(self.grid.x):
                for j, y in enumerate(self.grid.y):
                    if not always_cartesian:
                        coords = (self.rs[i,j], self.thetas[i,j], z) if self.cylindrical_geometry else (x, y, z)
                    else:
                        coords = (x, y, z)
                    r = func((i, j, k), coords)
                    if r:
                        res.append(r)
        return res

    def generate_trap(self):
        """generate pa file"""
        self._go_throw_volume(self.put_point)
        self.unrefined_pa.save(f"{self.pa_filename}.pa#")

    def refine_trap(self):
        """make refine procedure of SIMION"""
        subprocess.run([SIMION_LOCATION, NO_GUI_STR, REFINE_STR,
                        # "--convergence=5e-3",
                        f"{self.pa_filename}.pa#"])

        print("refine created")

    def new_adjust_rule(self, voltage) -> typing.Optional[int]:
        """you can use some other adjust rule for each trap. To do it re-define this method"""
        return voltage.to_adjust()

    def get_voltage_for_adj(self, t, adjust_rule: typing.Optional[typing.Callable] = None) -> float:
        outher_rule_pot = None
        if adjust_rule is not None:
            outher_rule_pot = adjust_rule(t)
        inner_rule_pot = self.new_adjust_rule(t)
        if outher_rule_pot is not None:
            potential = outher_rule_pot
        elif inner_rule_pot is not None:
            potential = inner_rule_pot
        else:
            potential = t.to_adjust()
        return potential

    def adjust_trap(self, adjust_rule: typing.Optional[typing.Callable] = None):
        """adjust the trap. Using the given rule ore the inner rule or the common rule"""
        voltages = []
        for t in self._voltages:
            potential = self.get_voltage_for_adj(t, adjust_rule)
            voltages.append(f"{t.value}={potential}")
        voltages = ",".join(voltages)
        print(voltages)
        self._adjust_trap(voltages)
        # voltages = ",".join([f"{v.name}={v.value}" for v in self._voltages])

    def _adjust_trap(self, voltages):
        """simion call for adjust trap"""
        cmd = [
            SIMION_LOCATION, NO_GUI_STR, ADJUST_STR, f"{self.pa_filename}.pa0",
            voltages
        ]
        print(subprocess.list2cmdline(cmd))
        subprocess.run(cmd)
        print("pa0 created")

    def load_adjusted_pa(self, ending="0"):
        self.pa = PA(file=f"{self.pa_filename}.pa{ending}")

    # def get_electrode_point(self, indexes, coords):
    #     i, j, k = indexes
    #     if self.pa.electrode(i, j, k):
    #         return (*coords, self.pa.potential_real(i, j, k))
    #     return None
    #
    # def get_potential_point(self, indexes, coords):
    #     return (*coords, self.pa.potential_real(*indexes))

    # def show_this_pot(self, coords: CoordsVar):
    #     return True
    #

