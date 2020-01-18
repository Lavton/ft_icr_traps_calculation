from traps.abstract_trap import Coords, CoordsVar
from .abstract_penning_with_simple_electrode_trap import AbstractPenningTrapWithSimpleElectrodes
from .voltage_enums import TrappedVoltages


class CuboidTrap(AbstractPenningTrapWithSimpleElectrodes):

    name = "cuboid"

    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return z >= self.trap_border.z

    def _is_other_electrode_simple(self, coords: CoordsVar):
        x, y, z = coords
        return x >= self.trap_border.x or y >= self.trap_border.y

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> TrappedVoltages:
        x, y, z = coords
        if x >= self.trap_border.x:
            return TrappedVoltages.DETECTION
        return TrappedVoltages.EXCITATION

    def __init__(self, x0, y0, z0, pa_file_name="test", *, pts=150
                 ):
        super().__init__(Coords(x0, y0, z0), pa_file_name=pa_file_name, pts=pts)

    def new_adjust_rule(self, voltage):
        if voltage.value == TrappedVoltages.TRAPPING.value:
            return 1 * 1.219

