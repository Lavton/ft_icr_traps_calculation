from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar, Voltages, TrappedVoltages


class CubicTrap(AbstractPenningTrapWithSimpleElectrodes):

    name = "Cubic"

    def _is_trapped_electrode_simple(self, coords: CoordsVar):
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

    def __init__(self, size: float, cell_name="test", *, pts=150
                 ):
        self.size = size
        super().__init__(Coords(size, size, size), cell_name=cell_name, pts=pts)

