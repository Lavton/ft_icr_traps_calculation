from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar
import numpy as np


class CylindricalTrap(AbstractPenningTrapWithSimpleElectrodes):
    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        return z >= self.cell_border.z

    def _is_other_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if r ** 2 < self.cell_border.x ** 2:
            return False
        else:
            return True

    def get_trap_electrode_type(self, coords: CoordsVar):
        return 2

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> int:
        r, theta, z = coords
        if 0 <= theta <= np.pi/2:
            return 1
        if np.pi <= theta <= np.pi*3/2:
            return 1
        return 3

    name = "cylindrical"

    def __init__(self, z0: float, a: float, cell_name="test", *, pts=150):
        super().__init__(Coords(x=a, y=a, z=z0), cell_name=cell_name, pts=pts, cylindrical_geometry=True)
