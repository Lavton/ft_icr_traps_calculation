from .cylindrical_trap import CylindricalTrap
from .abstract_trap import CoordsVar, Coords
from .voltage_enums import gen_voltage_enum
import numpy as np

_Voltages = gen_voltage_enum(2, 1)


class TolmachovTrap(CylindricalTrap):
    name = "tolmachov"
    _voltages = _Voltages

    def __init__(self, a: float, pa_file_name="test", pts=150):
        D = 2*a
        z0 = (0.25+0.2+0.2) * D
        self.zc1 = 0.2 * D
        self.zc2 = 0.2 * D
        self.ze = 1 * D

        bigger = 1.3
        model_border = Coords[float](
            x=bigger * a,
            y=bigger * a,
            z=bigger * (z0+self.ze)
        )
        super(TolmachovTrap, self).__init__(a=a, z0=z0, pa_file_name=pa_file_name, pts=pts, model_border=model_border)

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        if z < self.trap_border.z - self.zc1 - self.zc2:
            if 0 <= theta <= np.pi / 6:
                return self._voltages.EXCITATION
            return self._voltages.DETECTION
        elif z <= self.trap_border.z - self.zc2:
            return self._voltages.COMPENSATED_0
        elif z <= self.trap_border.z:
            return self._voltages.COMPENSATED_1
        else:
            return self._voltages.TRAPPING

    def new_adjust_rule(self, voltage):
        k = 2.3
        if voltage.value == self._voltages.COMPENSATED_0.value:
            return 0.1333*k
        if voltage.value == self._voltages.COMPENSATED_1.value:
            return 0.3167*k
        if voltage.value == self._voltages.TRAPPING.value:
            return 1*k
