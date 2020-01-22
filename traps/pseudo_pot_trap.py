from .abstract_trap import CoordsVar, Coords
from .voltage_enums import TrappedVoltages
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
import numpy as np


class PseudoPotentialTrap(AbstractPenningTrapWithSimpleElectrodes):
    name = "pseudo_potential_trap"
    _voltages = TrappedVoltages

    def __init__(self, z0: float, a: float, wire_num: int, pa_file_name="test", model_border=None, *, pts=150):
        self.wire_num = wire_num
        super().__init__(Coords(x=a, y=a, z=z0), pa_file_name=pa_file_name, pts=pts, cylindrical_geometry=False, model_border=model_border)
        self.wire_rad = self.gridstepmm * 1.1

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        w_step = self.trap_border.x / self.wire_num
        if z < self.trap_border.z:
            return False
        r, theta = np.sqrt(x**2+y**2), np.arctan2(y, x)
        if r ** 2 > self.trap_border.x ** 2:
            return False
        for i in range(self.wire_num):
            if (i * w_step - self.wire_rad) <= x <= (i * w_step + self.wire_rad):
                return True
        return False

    def _is_other_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        if z > self.trap_border.z:
            return False
        r, theta = np.sqrt(x**2+y**2), np.arctan2(y, x)
        if r ** 2 < self.trap_border.x ** 2:
            return False
        else:
            return True

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> TrappedVoltages:
        x, y, z = coords
        r, theta = np.sqrt(x ** 2 + y ** 2), np.arctan2(y, x)
        if 0 <= theta <= np.pi/4:
            return TrappedVoltages.EXCITATION
        return TrappedVoltages.DETECTION
