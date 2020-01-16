from .abstract_trap import AbstractTrap, CoordsVar
from abc import ABCMeta, abstractmethod
from .voltage_enums import TrappedVoltages, Voltages
import numpy as np
import typing


class AbstractPenningTrap(AbstractTrap, metaclass=ABCMeta):
    """
    class for penning traps - with trapped electrode, detection and excitation electrodes...
    """
    _voltages = TrappedVoltages

    def get_endcap_electrode_type(self, coords: CoordsVar) -> Voltages:
        """type of trap electrode. Can depends on coordinates"""
        return TrappedVoltages.TRAPPING

    def calculate_nontrap_electrode_type(self, coords: CoordsVar) -> Voltages:
        """non trap electrode type. Standard is equal 2 excitation and 2 detection electrodes"""
        r, theta, z = coords
        if 0 <= theta <= np.pi/4:
            return TrappedVoltages.EXCITATION
        return TrappedVoltages.DETECTION

    @abstractmethod
    def is_endcap_electrode(self, coords: CoordsVar) -> bool:
        """Check if electrode is a trapped end-cap electrode"""
        pass

    @abstractmethod
    def is_other_electrode(self, coords: CoordsVar) -> bool:
        """checked if it is a other electrode (it can be also trapped ones, but it is better to separate them"""
        pass

    def is_electrode(self, coords: CoordsVar) -> bool:
        """check if it is an electrode"""
        return self.is_endcap_electrode(coords) or self.is_other_electrode(coords)

    def get_electrode_type(self, coords: CoordsVar) -> int:
        """provide an electrode integer type"""
        if self.is_endcap_electrode(coords):
            e_type = self.get_endcap_electrode_type(coords)
        else:
            e_type = self.calculate_nontrap_electrode_type(coords)
        return e_type.value

    def put_point(self, indexes, coords):
        """put point inside the PA file on coordinate"""
        i, j, k = indexes
        if self.is_endcap_electrode(coords):
            e_type = self.get_endcap_electrode_type(coords)
            self.unrefined_pa.point(i, j, k, 1, e_type.value)
        elif self.is_other_electrode(coords):
            e_type = self.calculate_nontrap_electrode_type(coords)
            self.unrefined_pa.point(i, j, k, 1, e_type.value)

    def _color_for_3d(self, voltage: Voltages):
        if voltage == TrappedVoltages.EXCITATION:
            return "green", "Detection electrode"
        if voltage == TrappedVoltages.DETECTION:
            return "blue", "Excitation electrode"
        if voltage == TrappedVoltages.TRAPPING:
            return "red", "Trapping electrode"

