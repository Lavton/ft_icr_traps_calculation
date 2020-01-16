from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
from .abstract_trap import CoordsVar, Coords
from .voltage_enums import TrappedVoltages


class CubicTrap(AbstractPenningTrapWithSimpleElectrodes):

    name = "cubic"

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return z >= self.size

    def _is_other_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return x >= self.size or y >= self.size

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> TrappedVoltages:
        x, y, z = coords
        if x >= self.size:
            return TrappedVoltages.DETECTION
        return TrappedVoltages.EXCITATION

    def __init__(self, size: float, pa_file_name="test", *, pts=150
                 ):
        self.size = size
        super().__init__(Coords(size, size, size), pa_file_name=pa_file_name, pts=pts, cylindrical_geometry=False)


