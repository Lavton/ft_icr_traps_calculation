from .abstract_trap import CoordsVar, Coords
from .voltage_enums import CompensatedVoltages
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
import numpy as np


class WangTrap(AbstractPenningTrapWithSimpleElectrodes):
    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        pass

    def _is_other_electrode_simple(self, coords: CoordsVar):
        pass

    name = "wang_trap"
    _voltages = CompensatedVoltages

    def __init__(self, z0: float, a: float, delta_c: float, wire_num: int, pa_file_name="test", model_border=None, *, pts=150):
        self.wire_num = wire_num
        self.delta_c = delta_c
        super().__init__(Coords(x=a, y=a, z=z0), pa_file_name=pa_file_name, pts=pts, cylindrical_geometry=False, model_border=model_border)
        self.wire_rad = self.gridstepmm * 1.1

    def is_endcap_electrode(self, coords: CoordsVar) -> bool:
        x, y, z = coords
        r, theta = np.sqrt(x**2+y**2), np.arctan2(y, x)
        if r >= self.trap_border.x:
            return False
        return self.trap_border.z <= z <= self.trap_border.z + self.electrode_width
    
    def is_other_electrode(self, coords: CoordsVar) -> bool:
        w_step = self.trap_border.x / self.wire_num
        x, y, z = coords
        if z > self.trap_border.z:
            return False
        r, theta = np.sqrt(x ** 2 + y ** 2), np.arctan2(y, x)
        if r > self.trap_border.x + self.electrode_width:
            return False
        if r > self.trap_border.x:
            return True
        if self.trap_border.z - self.delta_c - self.electrode_width <= z <= self.trap_border.z - self.delta_c:
            for i in range(self.wire_num):
                if (i * w_step - self.wire_rad) <= x <= (i * w_step + self.wire_rad):
                    return True
            for i in range(self.wire_num):
                if (i * w_step - self.wire_rad) <= y <= (i * w_step + self.wire_rad):
                    return True
            return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar):
        x, y, z = coords
        r, theta = np.sqrt(x ** 2 + y ** 2), np.arctan2(y, x)
        if self.trap_border.x <= r <= self.trap_border.x + self.electrode_width:
            if 0 <= theta <= np.pi/4:
                return CompensatedVoltages.EXCITATION
            return CompensatedVoltages.DETECTION
        return CompensatedVoltages.COMPENSATED
