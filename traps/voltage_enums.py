from enum import Enum


class Voltages(Enum):
    def to_adust(self) -> int:
        pass


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