from .cylindrical_trap import CylindricalTrap
from .abstract_trap import CoordsVar, Coords
from .voltage_enums import CompensatedVoltages
import numpy as np

_Voltages = CompensatedVoltages


class KanawatyTrap(CylindricalTrap):
    name = "kanawaty"
    _voltages = _Voltages

    def __init__(self, a: float, pa_file_name="test", pts=150):
        or_r = 46/2
        or_z0 = 60/2
        or_ring_r = 10/2
        or_ring_z = 20
        z0 = or_z0 * a / or_r
        self.ring_r = or_ring_r * a / or_r
        self.ring_z = or_ring_z * a / or_r

        bigger = 1.3
        model_border = Coords[float](
            x=bigger * a,
            y=bigger * a,
            z=bigger * (z0+self.ring_z)
        )
        super(KanawatyTrap, self).__init__(a=a, z0=z0, pa_file_name=pa_file_name, pts=pts, model_border=model_border)

    def is_other_electrode(self, coords: CoordsVar) -> bool:
        r, theta, z = coords

        if z <= self.trap_border.z:
            return self.trap_border.x ** 2 <= r**2 <= (self.trap_border.x + self.electrode_width)**2
        else:
            if z <= self.trap_border.z + self.ring_z:
                return self.ring_r ** 2 <= r ** 2 <= (self.ring_r + self.electrode_width) ** 2

    def is_endcap_electrode(self, coords: CoordsVar) -> bool:
        r, theta, z = coords
        if r > self.trap_border.x:
            return False
        if r < self.ring_r:
            return False
        return self.trap_border.z <= z <= self.trap_border.z + self.electrode_width

    def calculate_nontrap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        if z <= self.trap_border.z:
            if 0 <= theta <= np.pi / 8:
                return self._voltages.EXCITATION
            if 3* np.pi / 8 <= theta <= np.pi / 2:
                return self._voltages.EXCITATION

            return self._voltages.DETECTION
        else:
            return CompensatedVoltages.COMPENSATED

    def new_adjust_rule(self, voltage):
        k = 0.335
        if voltage.value == self._voltages.TRAPPING.value:
            return 6*k
        if voltage.value == self._voltages.COMPENSATED.value:
            return 1*k
