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

    def _color_for_3d(self, voltage) -> Tuple[str, str]:
        if voltage.value == TrappedVoltages2.EXCITATION.value:
            return "green", "Detection electrode"
        if voltage.value == TrappedVoltages2.DETECTION.value:
            return "blue", "Excitation electrode"
        if voltage.value == TrappedVoltages2.TRAPPING.value:
            return "red", "Trapping electrode"
        if voltage.value == TrappedVoltages2.TRAPPING_B.value:
            return "red", "Trapping electrode"


def gen_voltage_enum(num_of_compensated=0, num_of_trapped=0):
    """use python magic for create new voltage enums dinamically"""
    voltages = {
        "EXCITATION": 1,
        "DETECTION": 2
    }
    color_descript = {
        1: ("green", "Detection electrode"),
        2: ("blue", "Excitation electrode")
    }
    adjust_dict = {
        1: 0,
        2: 0
    }
    last_num = 2
    compensated_colors = ["yellow", "gold", "goldenrod"]
    for i in range(num_of_compensated):

        voltages[f"COMPENSATED_{i}" if num_of_compensated > 1 else "COMPENSATED"] = last_num + 1
        color_descript[last_num + 1] = (compensated_colors[i], f"Compensated electrode {i+1}")
        adjust_dict[last_num + 1] = 0
        last_num += 1
    trapping_colors = ["red", "coral", "tomato", "salmon", "sienna"]
    for i in range(num_of_trapped):
        voltages[f"TRAPPING_{i}" if num_of_trapped > 1 else "TRAPPING"] = last_num + 1
        color_descript[last_num + 1] = (trapping_colors[i], f"Trapping electrode {i+1}")
        adjust_dict[last_num + 1] = 1
        last_num += 1
    DynamicEnum = Voltages(f"VoltagesC{num_of_compensated}T{num_of_trapped}", voltages)
    def _color_for_3d(self, voltage) -> Tuple[str, str]:
        return color_descript[voltage.value]
    DynamicEnum._color_for_3d = _color_for_3d
    def to_adjust(self) -> int:
        return adjust_dict[self.value]
    DynamicEnum.to_adjust = to_adjust
    return DynamicEnum

if __name__ == '__main__':
    e = gen_voltage_enum(2, 1)
    print(e.EXCITATION.colors_for_3d())
    print()