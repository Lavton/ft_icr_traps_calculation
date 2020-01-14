from traps.abstract_trap import AbstractPenningTrapWithSimpleElectrodes, Coords, CoordsVar, TrappedVoltages, Voltages
import numpy as np


class HyperbolicTrap(AbstractPenningTrapWithSimpleElectrodes):

    name = "hyperbolic"

    def __init__(self, z0: float, a: float, cell_name="test", *, pts=150):

        bigger = 3
        model_border = Coords[float](
            x=bigger * a,
            y=bigger * a,
            z=bigger * z0
        )
        self.r_max = 1.5*a
        super().__init__(Coords(x=a, y=a, z=z0), cell_name=cell_name, pts=pts, model_border=model_border,
                         cylindrical_geometry=True)

    def _is_trapped_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        # z *= 1.05
        if r > self.r_max:
            return False
        return 2*z**2 - r**2 >= 2*self.cell_border.z**2

    def _is_other_electrode_simple(self, coords: CoordsVar):
        r, theta, z = coords
        if r > self.r_max:
            return False
        return r**2 - 2*z**2 >= self.cell_border.x**2

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
        r, theta, z = coords
        if 0 <= theta <= np.pi/4:
            return TrappedVoltages.EXCITATION
        # if np.pi <= theta <= np.pi*3/2:
        #     return TrappedVoltages.EXCITATION
        return TrappedVoltages.DETECTION

    @staticmethod
    def new_adjust_rule(voltage):
        if voltage.value == TrappedVoltages.EXCITATION.value:
            return 0
        if voltage.value == TrappedVoltages.DETECTION.value:
            return 0
        if voltage.value == TrappedVoltages.TRAPPING.value:
            return 1*3*0.223*0.988
