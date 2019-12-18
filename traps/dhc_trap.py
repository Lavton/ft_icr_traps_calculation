from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar, TrappedVoltages, Voltages
from traps.cylindrical_trap import CylindricalTrap
import numpy as np

class TrappedVoltages2(Voltages):
    EXCITATION = 1
    DETECTION = 2
    TRAPPING = 3
    TRAPPING_B = 4

    def to_adjust(self) -> int:
        if self == self.DETECTION:
            return 0
        if self == self.EXCITATION:
            return 0
        if self == self.TRAPPING:
            return 1
        if self == self.TRAPPING_B:
            return 1

class DHCTrap(CylindricalTrap):

    name = "DHC"
    _voltages = TrappedVoltages2

    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        """
        Check, if the point (x,y,z) is inside the electrode at the end of the DHC.
        This happens when 2*z^2 - r^2 >= 2*z0^2 - R^2
        """
        r, theta, z = coords
        # z *= 1.05 # for view
        # if z >= self.cell_border.z:
        #     return True  ## open cell with grounded end
        # return False  ## for Open cell we have no hat!
        if 2 * z ** 2 - (r ** 2) >= 2 * self.cell_border.z ** 2 - self.cell_border.x ** 2:
            return True
        else:
            return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
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
                return self._voltages.TRAPPING_B
            if l <= theta+2*np.pi <= r:
                return self._voltages.TRAPPING_B
        if 0 <= theta <= np.pi/4:
            return self._voltages.EXCITATION
        # if np.pi <= theta <= np.pi*3/2:
        #     return TrappedVoltages.EXCITATION
        return self._voltages.DETECTION

    def _color_for_3d(self, voltage: Voltages):
        if voltage == TrappedVoltages2.EXCITATION:
            return "green", "Detection electrode"
        if voltage == TrappedVoltages2.DETECTION:
            return "blue", "Excitation electrode"
        if voltage == TrappedVoltages2.TRAPPING:
            return "red", "Trapping electrode"
        if voltage == TrappedVoltages2.TRAPPING_B:
            return "red", "Trapping electrode"

    @staticmethod
    def new_adjust_rule(voltage):
        if voltage.value == TrappedVoltages2.TRAPPING.value or voltage.value == TrappedVoltages2.TRAPPING_B.value:
            return 3.10
        else:
            return 0


