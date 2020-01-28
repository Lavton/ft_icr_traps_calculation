from .cylindrical_trap import CylindricalTrap
from .voltage_enums import gen_voltage_enum
from .abstract_trap import Coords, CoordsVar
import numpy as np

_Voltages = gen_voltage_enum(0, 2)


class OpenCylindricalTrap(CylindricalTrap):
    name = "open_trap"
    _voltages = _Voltages

    def __init__(self, a: float, z0: float, ze: float, pa_file_name="test", *, pts=150):
        self.ze = ze

        bigger = 1.3
        model_border = Coords[float](
            x=bigger * a,
            y=bigger * a,
            z=bigger * (z0+ze)
        )
        super().__init__(z0=z0, a=a, pa_file_name=pa_file_name, pts=pts, model_border=model_border)

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        if z < self.trap_border.z:
            if 0 <= theta <= np.pi / 4:
                return self._voltages.EXCITATION
            return self._voltages.DETECTION
        else:
            if 0 <= theta <= np.pi / 4:
                return self._voltages.TRAPPING_0
            return self._voltages.TRAPPING_1

