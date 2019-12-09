import os
import subprocess
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import typing
import numpy as np
from math import ceil
from tqdm import tqdm as tqdm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from SIMION.PA import PA
from enum import Enum, auto
T = typing.TypeVar('T')


@dataclass
class Coords(typing.Generic[T]):
    x: T
    y: T
    z: T


CoordsVar = typing.Tuple[float, float, float]  # (x, y, z) или (r, theta, z)


class Voltages(Enum):
    pass


class SimpleVoltages(Voltages):
    EXCITATION = auto()
    DETECTION = auto()


class TrappedVoltages(Voltages):
    EXCITATION = auto()
    DETECTION = auto()
    TRAPPING = auto()


class AbstractTrap(metaclass=ABCMeta):

    name = "abstract"
    _voltages = Voltages

    def _create_geometry(
            self, cell_border: Coords[float],
            *, pts=150, model_border: typing.Optional[Coords[float]] =None,
            cylindrical_geometry=False
    ):
        # первое, что надо сделать: определить точные параметры модели.
        # по умолчанию они немного (в 1.3 раза) больше размера ловушки
        # по после этого надо их слегка поправить так, чтобы в размер укладывалось целое число шагов сетки
        model_border = model_border if model_border else Coords[float](
            x=1.3 * cell_border.x,
            y=1.3 * cell_border.y,
            z=1.3 * cell_border.z
        )
        self.pts = pts
        gridstepmm = model_border.x / pts
        # теперь слегка поправим все координаты так, чтобы в них укладывалось целое число gridstepmm
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
        self.cell_border = cell_border
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

    def __init__(
            self, cell_border: Coords[float], cell_name="test", *,
            pts=150, model_border: typing.Optional[Coords[float]] =None,
            cylindrical_geometry=False
    ):
        self.cell_name = cell_name
        self.cylindrical_geometry = cylindrical_geometry
        self._standard_direction = {0, 1, 2} if not cylindrical_geometry else {0, 2}
        self._create_geometry(cell_border,
                              pts=pts, model_border=model_border, cylindrical_geometry=cylindrical_geometry)
        self.unrefined_pa = PA(
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
        self.pa = self.unrefined_pa

    def _gen_coords_for_test(self, coords: CoordsVar, directions: typing.Set, width):
        directions = list(directions)
        for i, direction in enumerate(directions):
            new_coords = list(coords)
            new_coords[direction] *= (1-width)
            yield tuple(new_coords)
            for j in range(i+1, len(directions)):
                new_coords = list(coords)
                new_coords[direction] *= (1 - width)
                new_coords[directions[j]] *= (1-width)
                yield tuple(new_coords)
                for k in range(j+1, len(directions)):
                    new_coords = list(coords)
                    new_coords[direction] *= (1 - width)
                    new_coords[directions[j]] *= (1 - width)
                    new_coords[directions[k]] *= (1-width)
                    yield tuple(new_coords)

    def _cut_electrode(self, coords: CoordsVar, simple_condition: typing.Callable[[CoordsVar], bool],
                       directions: typing.Optional[typing.Set]=None, width=0.05
                       ):
        if not simple_condition(coords):
            return -1
        if directions is None:
            directions = self._standard_direction
        for coords in self._gen_coords_for_test(coords, directions, width=width):
            if not simple_condition(coords):
                return 0
        return 1

    @abstractmethod
    def is_electrode(self, coords: CoordsVar):
        pass

    @abstractmethod
    def get_electrode_type(self, coords: CoordsVar) -> int:
        pass

    def put_point(self, indexes, coords):
        i, j, k = indexes
        if self.is_electrode(coords):
            self.unrefined_pa.point(i, j, k, 1, self.get_electrode_type(coords))

    def _go_throw_volume(self, func: typing.Callable[[typing.Tuple[int, int, int], CoordsVar], typing.Any],
                         always_cartesian=False):
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

    def generate_cell(self):
        self._go_throw_volume(self.put_point)
        self.unrefined_pa.save(f"{self.cell_name}.pa#")

    def refine_cell(self):
        simion_location = os.path.abspath("SIMION-8.1/simion.exe")
        subprocess.run([simion_location, "--nogui", "refine", "--convergence=5e-3", f"{self.cell_name}.pa#"])

        print("refine created")

    def adjust_cell(self):
        voltages = ",".join([f"{k}={v}" for (k, v) in self._voltages.items()])
        self._adjust_cell(voltages)

    def _adjust_cell(self, voltages):
        simion_location = os.path.abspath("SIMION-8.1/simion.exe")
        cmd = [
            simion_location, "--nogui", "fastadj", f"{self.cell_name}.pa0",
            voltages
        ]
        print(subprocess.list2cmdline(cmd))
        subprocess.run(cmd)
        print("pa0 created")

    def load_adjusted_pa(self):
        self.pa = PA(file=f"{self.cell_name}.pa0")

    def get_electrode_point(self, indexes, coords):
        i, j, k = indexes
        if self.pa.electrode(i, j, k):
            return (*coords, self.pa.potential_real(i, j, k))
        return None

    def get_potential_point(self, indexes, coords):
        return (*coords, self.pa.potential_real(*indexes))

    def show_this_pot(self, coords: CoordsVar):
        return True

    def _unbend_dimention(self, what, coef1, coef2, abs=False):
        f = lambda coef: np.abs(coef) if abs else coef

        return np.array(list(f(coef1)*what[::coef1]) + list(f(coef2)*what[::coef2]))

    def unbend_space(self, xs, ys, zs, potentials):
        # first
        xs = self._unbend_dimention(xs, -1, 1)
        ys = self._unbend_dimention(ys, 1, 1)
        zs = self._unbend_dimention(zs, 1, 1)
        potentials = self._unbend_dimention(potentials, -1, 1, abs=True)
        # second
        xs = self._unbend_dimention(xs, 1, 1)
        ys = self._unbend_dimention(ys, -1, 1)
        zs = self._unbend_dimention(zs, 1, 1)
        potentials = self._unbend_dimention(potentials, -1, 1, abs=True)
        # third
        xs = self._unbend_dimention(xs, 1, 1)
        ys = self._unbend_dimention(ys, 1, 1)
        zs = self._unbend_dimention(zs, -1, 1)
        potentials = self._unbend_dimention(potentials, -1, 1, abs=True)
        # print(xs.shape, ys.shape, zs.shape, potentials.shape)
        return xs, ys, zs, potentials

    def plot_3D_electrodes(self):
        # https://stackoverflow.com/questions/12904912/how-to-set-camera-position-for-3d-plots-using-python-matplotlib
        data = self._go_throw_volume(self.get_electrode_point, always_cartesian=True)
        data = np.array(data)
        xs = data[:, 0]
        ys = data[:, 1]
        zs = data[:, 2]
        voltage = data[:, 3]
        # xs, ys, zs, voltage = self.unbend_space(xs, ys, zs, voltage)  # TODO: make it works...

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        img = ax.scatter(xs[::15], ys[::15], zs[::15], c=voltage[::15], cmap=plt.hot())
        fig.colorbar(img)
        plt.show()

        # plt.savefig("test.png")

    def _get_float_ind(self, coords: Coords[float]) -> Coords[float]:
        return Coords(
            x=coords.x / self.gridstepmm,
            y=coords.y / self.gridstepmm,
            z=coords.z / self.gridstepmm
        )

    def _numerical_phi_cartesian(self, coords: Coords[float]):
        # тут мы усредняем значение на узлах сетки, чтобы получить значение на границе
        indexes_float = self._get_float_ind(coords)
        i = int(np.floor(indexes_float.x))
        j = int(np.floor(indexes_float.y))
        k = int(np.floor(indexes_float.z))
        alpha = indexes_float.x - i
        betta = indexes_float.y - j
        gamma = indexes_float.z - k
        p000 = self.pa.potential_real(x=i, y=j, z=k)
        p001 = self.pa.potential_real(x=i, y=j, z=k + 1)
        p010 = self.pa.potential_real(x=i, y=j + 1, z=k)
        p011 = self.pa.potential_real(x=i, y=j + 1, z=k + 1)
        p100 = self.pa.potential_real(x=i + 1, y=j, z=k)
        p101 = self.pa.potential_real(x=i + 1, y=j, z=k + 1)
        p110 = self.pa.potential_real(x=i + 1, y=j + 1, z=k)
        p111 = self.pa.potential_real(x=i + 1, y=j + 1, z=k + 1)
        #     return p000
        return (
                +(alpha) * (betta) * (gamma) * p111
                + (alpha) * (1 - betta) * (gamma) * p101
                + (alpha) * (betta) * (1 - gamma) * p110
                + (alpha) * (1 - betta) * (1 - gamma) * p100
                + (1 - alpha) * (betta) * (gamma) * p011
                + (1 - alpha) * (1 - betta) * (gamma) * p001
                + (1 - alpha) * (betta) * (1 - gamma) * p010
                + (1 - alpha) * (1 - betta) * (1 - gamma) * p000
        )

    def _numerical_phi_cilindrical(self, z, r, theta):
        x = r*np.cos(theta)
        y = r*np.sin(theta)
        return self._numerical_phi_cartesian(Coords(x, y, z))

    def _get_averaged_phi_point(self, zfrac, rfrac, num_th=0):
        if not num_th:
            num_th = int(self.pts*np.pi/2)
        z = zfrac*self.cell_border.z
        r = rfrac*self.cell_border.x
        # усреднённое поле практическое
        return np.mean(np.array(
            [self._numerical_phi_cilindrical(z, r, theta) for theta in np.linspace(0, np.pi/2, num_th)]
        ))

    def get_averaged_phi(self):
        rs = np.linspace(0, 1, 10)
        plt.plot(rs, [self._get_averaged_phi_point(0.2, r) for r in rs])
        plt.show()
        pass


class AbstractPenningTrap(AbstractTrap, metaclass=ABCMeta):
    _voltages = TrappedVoltages

    # @abstractmethod
    def get_trap_electrode_type(self, coords: CoordsVar) -> Voltages:
        return TrappedVoltages.TRAPPING
        # pass

    @abstractmethod
    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
        pass

    @abstractmethod
    def is_trapped_electrode(self, coords: CoordsVar) -> bool:
        pass

    @abstractmethod
    def is_other_electrode(self, coords: CoordsVar) -> bool:
        pass

    def is_electrode(self, coords: CoordsVar):
        return self.is_trapped_electrode(coords) or self.is_other_electrode(coords)

    def get_electrode_type(self, coords: CoordsVar) -> int:
        if self.is_trapped_electrode(coords):
            e_type = self.get_trap_electrode_type(coords)
        else:
            e_type = self.calculate_nontrap_electrode_type(coords)
        return self.voltages_to_int(e_type)

    def voltages_to_int(self, e_type: Voltages) -> int:
        for i, t in enumerate(self._voltages):
            if t == e_type:
                return i + 1

    def put_point(self, indexes, coords):
        i, j, k = indexes
        if self.is_trapped_electrode(coords):
            e_type = self.get_trap_electrode_type(coords)
            self.unrefined_pa.point(i, j, k, 1, self.voltages_to_int(e_type))
        elif self.is_other_electrode(coords):
            e_type = self.calculate_nontrap_electrode_type(coords)
            self.unrefined_pa.point(i, j, k, 1, self.voltages_to_int(e_type))


class AbstractPenningTrapWithSimpleElectrodes(AbstractPenningTrap, metaclass=ABCMeta):
    @abstractmethod
    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        pass

    @abstractmethod
    def _is_other_electrode_simple(self, coords: CoordsVar):
        pass

    def _cut_trapped(self, coords):
        return self._cut_electrode(coords, self._is_trapped_electrode_simple, {2})

    def _cut_other(self, coords):
        if self.cylindrical_geometry:
            directions = {0}
        else:
            directions = {0, 1}
        return self._cut_electrode(coords, self._is_other_electrode_simple, directions)

    def is_trapped_electrode(self, coords: CoordsVar) -> bool:
        if self._cut_trapped(coords) == 0:
            if self._cut_other(coords) <= 0:
                return True
        return False

    def is_other_electrode(self, coords: CoordsVar) -> bool:
        if self._cut_other(coords) == 0:
            if self._cut_trapped(coords) <= 0:
                return True
        return False

    def show_this_pot(self, coords: CoordsVar):
        return self._cut_other(coords) <= 0 and self._cut_trapped(coords) <= 0
