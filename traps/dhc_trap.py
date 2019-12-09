from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar, TrappedVoltages
from traps.cylindrical_trap import CylindricalTrap
import numpy as np


class DHCTrap(CylindricalTrap):

    name = "DHC"

    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        """
        Check, if the point (x,y,z) is inside the electrode at the end of the DHC.
        This happens when 2*z^2 - r^2 >= 2*z0^2 - R^2
        """
        r, theta, z = coords
        # if z >= self.cell_border.z:
        #     return True  ## open cell with grounded end
        # return False  ## for Open cell we have no hat!
        if 2 * z ** 2 - (r ** 2) >= 2 * self.cell_border.z ** 2 - self.cell_border.x ** 2:
            return True
        else:
            return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> int:
        r, theta, z = coords
        return self._get_electrode_type(theta, z)

    def __init__(self, z0: float, a: float, N: int=8, beta: float = 1, cell_name="test", *, pts=150):
        self.N = N
        self.beta = beta
        self.alpha_0 = beta*np.pi/N
        super().__init__(z0=z0, a=a, cell_name=cell_name, pts=pts)

    def _get_phi_arias(self, n, z):
        """get the area, where there is voltage"""
        N, z0 = self.N, self.cell_border.z
        center = 2 * np.pi * (n + 1.0 / 2) / N
        delta_ = np.pi / N + self.alpha_0 * ((z / z0) ** 2 - 1)
        return center - delta_, center + delta_

    def _get_electrode_type(self, theta, z):
        """get electrode type on this angle theta"""
        # self.voltages.put(1)
        # self.voltages.put(2)
        N, z0 = self.N, self.cell_border.z
        for n in range(N):
            l, r = self._get_phi_arias(n, z)
            if l <= theta <= r:
                return TrappedVoltages.TRAPPING
            if l <= theta+2*np.pi <= r:
                return TrappedVoltages.TRAPPING
        if 0 <= theta <= np.pi/4:
            return TrappedVoltages.EXCITATION
        # if np.pi <= theta <= np.pi*3/2:
        #     return TrappedVoltages.EXCITATION
        return TrappedVoltages.DETECTION

