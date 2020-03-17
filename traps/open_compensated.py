from .cylindrical_trap import CylindricalTrap
from .voltage_enums import CompensatedVoltages
from .abstract_trap import Coords, CoordsVar
import numpy as np


class OpenCompensatedCylindricalTrap(CylindricalTrap):
    name = "open_compesated"
    _voltages = CompensatedVoltages

    def __init__(self, z0: float, a: float, dzc: float, ze: float, pa_file_name="test", *, pts=150):
        self.ze = ze
        self.dzc = dzc

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
        if z < self.trap_border.z - self.dzc:
            return super(OpenCompensatedCylindricalTrap, self).calculate_nontrap_electrode_type(coords)
        elif z <= self.trap_border.z:
            return CompensatedVoltages.COMPENSATED
        else:
            return CompensatedVoltages.TRAPPING

    def new_adjust_rule(self, voltage):
        if voltage.value == CompensatedVoltages.TRAPPING.value:
            return 1.949
        if voltage.value == CompensatedVoltages.COMPENSATED.value:
            return 0.3235

    def dkdvc(self, k):
        """calculate V_0 * d A_{k0}/ d V_c"""
        from scipy.special import factorial, jv
        before_sum = ((-1)**(k/2) /factorial(k)) * (np.pi**(k-1) / (2 ** (k-3))) * (self.get_d()/(self.trap_border.z+self.ze))**k

        def in_sum(n):
            kn = (n+0.5) * np.pi / (self.trap_border.z + self.ze)
            a_nd = np.sin(kn*self.trap_border.z) - np.sin(kn*(self.trap_border.z - self.dzc))
            part = (2*n+1)**(k-1) * a_nd / jv(0, 1j*kn*self.trap_border.x).real
            return part
        max_n = 100
        return before_sum * sum((in_sum(n) for n in range(max_n)))

    def a_k(self, k):
        from scipy.special import factorial, jv
        before_sum = ((-1)**(k/2) /factorial(k)) * (np.pi**(k-1) / (2 ** (k-3))) * (self.get_d()/(self.trap_border.z+self.ze))**k

        def in_sum(n):
            kn = (n+0.5) * np.pi / (self.trap_border.z + self.ze)
            a_nc = (-1)**n - np.sin(kn*self.trap_border.z) - np.sin(kn*(self.trap_border.z - self.dzc))
            part = (2*n+1)**(k-1) * a_nc / jv(0, 1j*kn*self.trap_border.x).real
            return part
        max_n = 100
        return before_sum * sum((in_sum(n) for n in range(max_n)))
