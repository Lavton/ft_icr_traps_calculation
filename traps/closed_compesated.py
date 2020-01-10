from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar, TrappedVoltages, Voltages
from traps.cylindrical_trap import CylindricalTrap
import numpy as np


class TrappedVoltagesCompensated(Voltages):
    EXCITATION = 1
    DETECTION = 2
    TRAPPING = 3
    COMPENSATED = 4

    def to_adjust(self) -> int:
        if self == self.DETECTION:
            return 0
        if self == self.EXCITATION:
            return 0
        if self == self.TRAPPING:
            return 1
        if self == self.COMPENSATED:
            return 10


class ClosedCompesatedCylindricalTrap(CylindricalTrap):
    name = "ClosedCompensated"
    _voltages = TrappedVoltagesCompensated

    def __init__(self, R: float, dz2z_ratio: float = 0.3, z2r_ratio: float = 1.16,  cell_name="test", *, pts=150):
        z0 = R/z2r_ratio
        dzc = z0*dz2z_ratio
        self.dzc = dzc
        super().__init__(z0=z0, a=R, cell_name=cell_name, pts=pts)

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
        r, theta, z = coords
        if z < self.cell_border.z - self.dzc:
            return super(ClosedCompesatedCylindricalTrap, self).calculate_nontrap_electrode_type(coords)
        else:
            return TrappedVoltagesCompensated.COMPENSATED

    def _color_for_3d(self, voltage: Voltages):
        if voltage == TrappedVoltagesCompensated.EXCITATION:
            return "green", "Detection electrode"
        if voltage == TrappedVoltagesCompensated.DETECTION:
            return "blue", "Excitation electrode"
        if voltage == TrappedVoltagesCompensated.TRAPPING:
            return "red", "Trapping electrode"
        if voltage == TrappedVoltagesCompensated.COMPENSATED:
            return "yellow", "Compensated electrode"

    @staticmethod
    def new_adjust_rule(voltage):
        if voltage.value == TrappedVoltagesCompensated.EXCITATION.value:
            return 0
        if voltage.value == TrappedVoltagesCompensated.DETECTION.value:
            return 0
        if voltage.value == TrappedVoltagesCompensated.TRAPPING.value:
            return 0.7323
        if voltage.value == TrappedVoltagesCompensated.COMPENSATED.value:
            return 0.7323 * 0.05
