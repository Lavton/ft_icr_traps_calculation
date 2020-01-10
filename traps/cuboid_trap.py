from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar, Voltages, TrappedVoltages


class CuboidTrap(AbstractPenningTrapWithSimpleElectrodes):

    name = "cuboid"

    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return z >= self.cell_border.z

    def _is_other_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return x >= self.cell_border.x or y >= self.cell_border.y

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> TrappedVoltages:
        x, y, z = coords
        if x >= self.cell_border.x:
            return TrappedVoltages.DETECTION
        return TrappedVoltages.EXCITATION

    def __init__(self, x0, y0, z0, cell_name="test", *, pts=150
                 ):
        super().__init__(Coords(x0, y0, z0), cell_name=cell_name, pts=pts)

    @staticmethod
    def new_adjust_rule(voltage):
        if voltage.value == TrappedVoltages.EXCITATION.value:
            return 0
        if voltage.value == TrappedVoltages.DETECTION.value:
            return 0
        if voltage.value == TrappedVoltages.TRAPPING.value:
            return 1.2

