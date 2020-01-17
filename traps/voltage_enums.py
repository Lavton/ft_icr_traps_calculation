from enum import Enum
from typing import Tuple


class Voltages(Enum):
    def to_adust(self) -> int:
        pass

    def _color_for_3d(self, voltage) -> Tuple[str, str]:
        """provides the color and desciption based on electrode type"""
        pass

    def colors_for_3d(self):
        return {v.value: self._color_for_3d(v)[0] for v in self.__class__}

    def legend_for_3d(self):
        return {self._color_for_3d(v)[0]: self._color_for_3d(v)[1] for v in self.__class__}


class SimpleVoltages(Voltages):
    EXCITATION = 1
    DETECTION = 2

    def to_adjust(self) -> int:
        if self == self.DETECTION:
            return 0
        if self == self.EXCITATION:
            return 1


class TrappedVoltages(Voltages):
    EXCITATION = 1
    DETECTION = 2
    TRAPPING = 3

    def to_adjust(self) -> int:
        if self == self.DETECTION:
            return 0
        if self == self.EXCITATION:
            return 0
        if self == self.TRAPPING:
            return 1

    def _color_for_3d(self, voltage) -> Tuple[str, str]:
        if voltage.value == self.EXCITATION.value:
            return "green", "Detection electrode"
        if voltage.value == self.DETECTION.value:
            return "blue", "Excitation electrode"
        if voltage.value == self.TRAPPING.value:
            return "red", "Trapping electrode"

class CompensatedVoltages(Voltages):
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
            return 2

    def _color_for_3d(self, voltage) -> Tuple[str, str]:
        if voltage.value == CompensatedVoltages.EXCITATION.value:
            return "green", "Detection electrode"
        if voltage.value == CompensatedVoltages.DETECTION.value:
            return "blue", "Excitation electrode"
        if voltage.value == CompensatedVoltages.TRAPPING.value:
            return "red", "Trapping electrode"
        if voltage.value == CompensatedVoltages.COMPENSATED.value:
            return "yellow", "Compensated electrode"
