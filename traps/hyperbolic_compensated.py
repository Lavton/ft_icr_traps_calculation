from .abstract_trap import CoordsVar
from .hyperbolic_trap import HyperbolicTrap
import numpy as np
from .voltage_enums import Voltages, CompensatedVoltages


class HyperbolicCompensatedTrap(HyperbolicTrap):

    name = "hyperbolic_compensated"
    _voltages = CompensatedVoltages

    def __init__(self, z0: float, a: float, rc: float, r_max: float, pa_file_name="test", *, pts=150):
        self.rc = rc
        super(HyperbolicCompensatedTrap, self).__init__(a=a, z0=z0, r_max=r_max, pa_file_name=pa_file_name, pts=pts)

    def _is_other_electrode_simple(self, coords: CoordsVar):
        return self._ring_simple(coords) or self._is_compensated_electrode_simple(coords)

    def _is_compensated_electrode_simple(self, coords: CoordsVar):
        # if in other electrodes - return
        if self._is_endcap_electrode_simple(coords):
            return False
        if self._ring_simple(coords):
            return False

        # intersection with ring:
        z_1 = np.sqrt((self.rc**2 - self.trap_border.x**2)/3)
        rho_1 = np.sqrt(self.rc**2 - z_1**2)
        theta_1 = np.arctan2(z_1, rho_1)

        # intersection with end-cap
        z_2 = np.sqrt((2 * self.trap_border.z**2 + self.rc**2)/3)
        rho_2 = np.sqrt(self.rc**2 - z_2**2)
        theta_2 = np.arctan2(z_2, rho_2)

        # point in the middle:
        middle_theta = (theta_1 + theta_2) / 2
        middle_z = self.rc * np.cos(middle_theta)
        middle_rho = self.rc * np.sin(middle_theta)
        r, theta, z = coords
        if r > self.r_max:
            return False
        if z >= -(middle_rho/middle_z) * (r - middle_rho) + middle_z:
            return True
        return False

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
        if self._is_compensated_electrode_simple(coords):
            return CompensatedVoltages.COMPENSATED
        r, theta, z = coords
        if 0 <= theta <= np.pi/4:
            return CompensatedVoltages.EXCITATION
        return CompensatedVoltages.DETECTION

    def new_adjust_rule(self, voltage):
        if voltage.value == CompensatedVoltages.EXCITATION.value:
            return 0
        if voltage.value == CompensatedVoltages.DETECTION.value:
            return 0
        if voltage.value == CompensatedVoltages.TRAPPING.value:
            return 0.7172 * 1.21
        if voltage.value == CompensatedVoltages.COMPENSATED.value:
            return 0.455

