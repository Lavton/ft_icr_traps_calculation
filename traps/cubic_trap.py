from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar


class CubicTrap(AbstractPenningTrapWithSimpleElectrodes):

    name = "Cubic"
    _voltages = {1: 0, 2: 1, 3: 0}

    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return z >= self.size

    def _is_other_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return x >= self.size or y >= self.size

    def get_trap_electrode_type(self, coords: CoordsVar):
        return 2

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> int:
        x, y, z = coords
        if x >= self.size:
            return 1
        return 3

    def __init__(self, size: float, cell_name="test", *, pts=150
                 ):
        self.size = size
        super().__init__(Coords(size, size, size), cell_name=cell_name, pts=pts)

