from traps.abstract_trap import Coords, CoordsVar
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
from .voltage_enums import TrappedVoltages
import numpy as np


class CylindricalTrap(AbstractPenningTrapWithSimpleElectrodes):
    name = "cylindrical"

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        return z >= self.trap_border.z

    def _is_other_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if r ** 2 < self.trap_border.x ** 2:
            return False
        else:
            return True

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> TrappedVoltages:
        r, theta, z = coords
        if 0 <= theta <= np.pi/4:
            return TrappedVoltages.EXCITATION
        # if np.pi <= theta <= np.pi*3/2:
        #     return TrappedVoltages.EXCITATION
        return TrappedVoltages.DETECTION

    def __init__(self, z0: float, a: float, pa_file_name="test", *, pts=150):
        super().__init__(Coords(x=a, y=a, z=z0), pa_file_name=pa_file_name, pts=pts, cylindrical_geometry=True)

    def new_adjust_rule(self, voltage):
        if voltage.value == TrappedVoltages.EXCITATION.value:
            return 0
        if voltage.value == TrappedVoltages.DETECTION.value:
            return 0
        if voltage.value == TrappedVoltages.TRAPPING.value:
            return 0.988
