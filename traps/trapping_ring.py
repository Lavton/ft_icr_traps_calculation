from traps.abstract_trap import Coords, CoordsVar
from traps.cylindrical_trap import CylindricalTrap
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
from .voltage_enums import gen_voltage_enum
import numpy as np

_Voltages = gen_voltage_enum(0, 5)


class TrappingRingTrap(CylindricalTrap):
    name = "trapping_ring"
    _voltages = _Voltages

    def __init__(self, a: float, pa_file_name="test", *, pts=150):
        self.ring_width = 0.110
        self.ring_space = 0.039
        self.orig_diam = 1.875
        self.orig_len = 2
        D = 2*a
        z0 = (self.orig_len / 2) * D / self.orig_diam
        self.ring_width *= D / self.orig_diam
        self.ring_space *= D / self.orig_diam
        self.last_offset = self.ring_space*2
        super().__init__(z0=z0, a=a, pa_file_name=pa_file_name, pts=pts)

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if z >= self.trap_border.z:
            return self._get_ring_number(r) > -1
        else:
            return False

    def get_endcap_electrode_type(self, coords: CoordsVar):
        r, theta, z = coords
        r_num = self._get_ring_number(r)
        if r_num == 0:
            return self._voltages.TRAPPING_0
        if r_num == 1:
            return self._voltages.TRAPPING_1
        if r_num == 2:
            return self._voltages.TRAPPING_2
        if r_num == 3:
            return self._voltages.TRAPPING_3
        if r_num == 4:
            return self._voltages.TRAPPING_4

    def _is_other_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if z >= self.trap_border.z:
            return False
        return super(TrappingRingTrap, self)._is_other_electrode_simple(coords)

    def _get_ring_number(self, r):
        first_offset = self.trap_border.x - self.last_offset + self.ring_space - 5 * (self.ring_space + self.ring_width)
        for i in range(0, 5):
            if first_offset + i * (self.ring_width + self.ring_space) <= r:
                if r <= first_offset + i * (self.ring_width + self.ring_space) + self.ring_width:
                    return i
        return -1

    def new_adjust_rule(self, voltage):
        k = 1
        if voltage.value == self._voltages.TRAPPING_0.value:
            return 0.2 * k
        if voltage.value == self._voltages.TRAPPING_1.value:
            return 1.1 * k
        if voltage.value == self._voltages.TRAPPING_2.value:
            return 2.0 * k
        if voltage.value == self._voltages.TRAPPING_3.value:
            return 2.4 * k
        if voltage.value == self._voltages.TRAPPING_4.value:
            return 2.8 * k
