from traps.abstract_trap import Coords, CoordsVar
from .voltage_enums import TrappedVoltages2
from traps.cylindrical_trap import CylindricalTrap
import numpy as np


class DHCTrap(CylindricalTrap):

    name = "DHC"
    _voltages = TrappedVoltages2

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        """
        Check, if the point (x,y,z) is inside the electrode at the end of the DHC.
        This happens when 2*z^2 - r^2 >= 2*z0^2 - R^2
        """
        r, theta, z = coords
        # z *= 1.05 # for 3D visualization with expanding
        if 2 * z ** 2 - (r ** 2) >= 2 * self.trap_border.z ** 2 - self.trap_border.x ** 2:
            return True
        else:
            return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> TrappedVoltages2:
        r, theta, z = coords
        return self._get_electrode_type(theta, z)

    def __init__(self, z0: float, a: float, N: int=8, beta: float = 1, pa_file_name="test", *, pts=150):
        self.N = N
        self.beta = beta
        self.alpha_0 = beta*np.pi/N
        super().__init__(z0=z0, a=a, pa_file_name=pa_file_name, pts=pts)

    def _get_phi_arias(self, n, z):
        """get the area, where there is voltage"""
        N, z0 = self.N, self.trap_border.z
        center = 2 * np.pi * (n + 1.0 / 2) / N
        delta_ = np.pi / N + self.alpha_0 * ((z / z0) ** 2 - 1)
        return center - delta_, center + delta_

    def _get_electrode_type(self, theta, z):
        """get electrode type on this angle theta"""
        N, z0 = self.N, self.trap_border.z
        for n in range(N):
            l, r = self._get_phi_arias(n, z)
            if l <= theta <= r:
                return self._voltages.TRAPPING_B
            if l <= theta+2*np.pi <= r:
                return self._voltages.TRAPPING_B
        if 0 <= theta <= np.pi/4:
            return self._voltages.EXCITATION
        return self._voltages.DETECTION

    def new_adjust_rule(self, voltage):
        if voltage.value == TrappedVoltages2.TRAPPING.value or voltage.value == TrappedVoltages2.TRAPPING_B.value:
            return 3.10
        else:
            return 0


