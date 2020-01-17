from traps.abstract_trap import Coords, CoordsVar
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
import numpy as np
from .voltage_enums import TrappedVoltages, Voltages


class HyperbolicTrap(AbstractPenningTrapWithSimpleElectrodes):
    name = "hyperbolic"

    def __init__(self, z0: float, a: float, r_max: float,  pa_file_name="test", *, pts=150):

        bigger = 1.3 * r_max / a
        model_border = Coords[float](
            x=bigger * a,
            y=bigger * a,
            z=bigger * z0
        )
        self.r_max = r_max
        super().__init__(Coords(x=a, y=a, z=z0), pa_file_name=pa_file_name, pts=pts, model_border=model_border,
                         cylindrical_geometry=True, electrode_width=3*1.6)

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        # z *= 1.05
        if r > self.r_max:
            return False
        return 2*z**2 - r**2 >= 2*self.trap_border.z**2

    def _is_other_electrode_simple(self, coords: CoordsVar):
        return self._ring_simple(coords)

    def _ring_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if r > self.r_max:
            return False
        return r**2 - 2*z**2 >= self.trap_border.x**2

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
        r, theta, z = coords
        if 0 <= theta <= np.pi/4:
            return TrappedVoltages.EXCITATION
        return TrappedVoltages.DETECTION

    def new_adjust_rule(self, voltage):
        if voltage.value == TrappedVoltages.TRAPPING.value:
            return 1 * 0.7172
        return None
