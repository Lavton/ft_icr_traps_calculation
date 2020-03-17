from .cylindrical_trap import CylindricalTrap
from .abstract_trap import CoordsVar, Coords
from .voltage_enums import gen_voltage_enum
import numpy as np

_Voltages = gen_voltage_enum(3, 1)


class BrustkernTrap(CylindricalTrap):
    name = "brustkern"
    _voltages = _Voltages

    def __init__(self, a: float, pa_file_name="test", pts=150):
        article_r = 31.24
        ext_det = 21.87 * a / article_r
        gap_size = 0.51 * a / article_r
        self.zc1 = 1.55 * a / article_r
        self.zc2 = 5.05 * a / article_r
        self.zc3 = 3.05 * a / article_r
        z0 = (ext_det + self.zc1 + self.zc2 + self. zc3 + gap_size * 4)
        self.ze = z0 * 4.2/2.8
        self.gap_size = gap_size

        bigger = 1.3
        model_border = Coords[float](
            x=bigger * a,
            y=bigger * a,
            z=bigger * (z0+self.ze)
        )
        super(BrustkernTrap, self).__init__(a=a, z0=z0, pa_file_name=pa_file_name, pts=pts, model_border=model_border)

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        return z >= self.trap_border.z + self.ze

    def calculate_nontrap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        sector = self.trap_border.z - self.zc1 - self.zc2 - self.zc3 - self.gap_size * 4
        if z < sector:
            if 0 <= theta <= np.pi / 4:
                return self._voltages.EXCITATION
            return self._voltages.DETECTION
        sector += self.gap_size + self.zc1
        if z <= sector:
            return self._voltages.COMPENSATED_0
        sector += self.gap_size + self.zc2
        if z <= sector:
            return self._voltages.COMPENSATED_1
        elif z <= self.trap_border.z - self.gap_size:
            return self._voltages.COMPENSATED_2
        else:
            return self._voltages.TRAPPING

    def get_endcap_electrode_type(self, coords: CoordsVar):
        """type of trap electrode. Can depends on coordinates"""
        return self._voltages.TRAPPING

    def _is_other_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if r ** 2 < self.trap_border.x ** 2:
            return False
        else:
            sector = self.trap_border.z - self.zc1 - self.zc2 - self.zc3 - self.gap_size * 4
            if sector < z < sector + self.gap_size:
                return False
            sector += self.gap_size + self.zc1
            if sector < z < sector + self.gap_size:
                return False
            sector += self.gap_size + self.zc2
            if sector < z < sector + self.gap_size:
                return False
            sector += self.gap_size + self.zc3
            if sector < z < sector + self.gap_size:
                return False
            sector = self.trap_border.z - self.gap_size
            if sector < z < sector + self.gap_size:
                return False
            return True

    def new_adjust_rule(self, voltage):
        k = 0.06269
        if voltage.value == self._voltages.COMPENSATED_0.value:
            return 9.608*k
        if voltage.value == self._voltages.COMPENSATED_1.value:
            return -7.608*k
        if voltage.value == self._voltages.COMPENSATED_2.value:
            return 9.608*k
        if voltage.value == self._voltages.TRAPPING.value:
            return 35*k
