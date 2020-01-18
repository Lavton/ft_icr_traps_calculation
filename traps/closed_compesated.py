from traps.abstract_trap import Coords, CoordsVar
from traps.cylindrical_trap import CylindricalTrap
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
from .voltage_enums import CompensatedVoltages
import numpy as np


class ClosedCompesatedCylindricalTrap(CylindricalTrap):
    name = "closed_compensated"
    _voltages = CompensatedVoltages

    def __init__(self, z0: float, a: float, dzc: float, pa_file_name="test", *, pts=150):
        # dzc = z0*dz2z_ratio
        self.dzc = dzc
        super().__init__(z0=z0, a=a, pa_file_name=pa_file_name, pts=pts)

    def calculate_nontrap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        if z < self.trap_border.z - self.dzc:
            return super(ClosedCompesatedCylindricalTrap, self).calculate_nontrap_electrode_type(coords)
        else:
            return CompensatedVoltages.COMPENSATED

    def new_adjust_rule(self, voltage):
        if voltage.value == CompensatedVoltages.TRAPPING.value:
            return 1.037
        if voltage.value == CompensatedVoltages.COMPENSATED.value:
            return  0.1455

    def dkdvc(self, k):
        """calculate V_0 * d A_{k0}/ d V_c"""
        from scipy.special import factorial, jv
        before_sum = ((-1)**k /factorial(k)) * (np.pi**(k-1) / 2 ** (k-3)) * (self.get_d()/self.trap_border.z)**k
        def in_sum(n):
            kn = (n+0.5) * np.pi / self.trap_border.z
            part = (-1)**n * (2*n+1)**(k-1) * 2*np.sin(0.5 * kn * self.dzc)**2 / jv(0, 1j*kn*self.trap_border.x).real
            return part
        max_n = 100
        return before_sum * sum((in_sum(n) for n in range(max_n)))
