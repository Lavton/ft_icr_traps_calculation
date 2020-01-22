from traps.abstract_trap import Coords, CoordsVar
from traps.cylindrical_trap import CylindricalTrap
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
from .voltage_enums import gen_voltage_enum
import numpy as np

_Voltages = gen_voltage_enum(0, 4)


class InfinityCell(CylindricalTrap):
    name = "infinity_cell"
    _voltages = _Voltages

    def __init__(self, z0: float, a: float, pa_file_name="test", *, pts=150):
        self.levels = [0, 0.1, 0.2, 0.4, 1]
        super().__init__(z0=z0, a=a, pa_file_name=pa_file_name, pts=pts)

    def get_endcap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        # theta += np.pi/4
        inf_trap_potential = self._get_infinity_trap_potential(r, self.trap_border.x, theta)
        if np.abs(inf_trap_potential) < self.levels[1]:
            return self._voltages.TRAPPING_0
        if self.levels[1] <= np.abs(inf_trap_potential) < self.levels[2]:
            return self._voltages.TRAPPING_1
        if self.levels[2] <= np.abs(inf_trap_potential) < self.levels[3]:
            return self._voltages.TRAPPING_2
        # if self.levels[3] <= np.abs(inf_trap_potential) < self.levels[4]:
        #     return self._voltages.TRAPPING_3
        # if self.levels[4] <= np.abs(inf_trap_potential):
        return self._voltages.TRAPPING_3

    @staticmethod
    def _get_infinity_trap_potential(r, R, _phi, max_n=100):
        alpha = np.pi/4
        phi = _phi - np.pi/2

        def under_sum(n):
            k = 2 * n + 1
            f = (r / R) ** k
            s = 2 * np.sin(k * alpha) / (k * np.pi)
            t = np.cos(k * phi)
            return f * s * t
        return sum([under_sum(i) for i in range(max_n)])

    def new_adjust_rule(self, voltage):
        k = 7.7821
        if voltage.value == self._voltages.TRAPPING_0.value:
            return (self.levels[0] + self.levels[1])*k/2
        if voltage.value == self._voltages.TRAPPING_1.value:
            return (self.levels[1] + self.levels[2])*k/2
        if voltage.value == self._voltages.TRAPPING_2.value:
            return (self.levels[2] + self.levels[3])*k/2
        if voltage.value == self._voltages.TRAPPING_3.value:
            return (self.levels[3] + self.levels[4])*k/2
