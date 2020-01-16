from .abstract_trap import CoordsVar, Coords
from .abstract_penning_trap import AbstractPenningTrap
from abc import ABCMeta, abstractmethod
import typing
from .voltage_enums import TrappedVoltages, Voltages


class AbstractPenningTrapWithSimpleElectrodes(AbstractPenningTrap, metaclass=ABCMeta):
    """
    Ok, it will be pretty hard to explain HOW this code works. But it has the simple goal.
    In some traps the only think it is needed to construct an electric field inside the trap is the inner surface
     of the electrode.
    Thus, only inner surface has the physical meaning and need to be created by hands. And it can be done in the
    simplest way by checking the inequality of this inner surface. For example: `z >= z_0`

    But you can't have 3D visualisation of such trap -- it will be just cuboid with a hole.
    That is why in common case you need to have electrode not `z >= z_0`, but `z_0+dz >= z >= z_0` for each and every
    electrode. The goal of this code is to create the second border automatically. So
    You set:
    .................|------------------------------------------ (fig 1)
    (where . is free space, | is border, - is electrode)
    the program creates
    .................|--|....................................... (fig 2)

    It is done in general the following way:
    If the current point is not an electrode by condition (before `|` if fig. 1)
     it will still not be an electrode in fig. 2
    If we are right from the `|` in fig. 1, but not VERY far from it
    not very far means that if we go by `width` to the left the simple condition will show, that it is not an electrode
                         V                                V
      .................|-------------  -> .................|-------------
    than it will be a new electrode.
    If we far away from `|`
                              V                                V
      .................|-------------  -> .................|-------------
    and new point will still be an electrode in simple condition, than in new one it will not be an electrode.
    """
    
    def __init__(self, trap_border: Coords[float], pa_file_name="test", *,
            pts=150, model_border: typing.Optional[Coords[float]] =None,
            cylindrical_geometry=False, electrode_width=1.6):

        self.electrode_width = electrode_width
        self._standard_direction = {0, 1, 2} if not cylindrical_geometry else {0, 2}
        super(AbstractPenningTrapWithSimpleElectrodes, self).__init__(
            trap_border=trap_border, pa_file_name=pa_file_name,
            pts=pts, model_border=model_border, cylindrical_geometry=cylindrical_geometry
        )

    def _gen_coords_for_test(self, coords: CoordsVar, directions: typing.Set, width):
        """return coords near by to check them in `simple_condition`."""
        # if simple condition is:
        # .................|------------------------------------------
        # we generate for test coordinate just before condition: like
        #                 |
        #                 V
        # .................|------------------------------------------

        # we use "direction" to work both with catesian and cylindrical
        directions = list(directions)
        # check in all directions -- for 1D, 2D or 3D
        for i, direction in enumerate(directions):
            new_coords = list(coords)
            new_coords[direction] -= width
            yield tuple(new_coords)
            for j in range(i+1, len(directions)):
                new_coords = list(coords)
                new_coords[direction] -= width
                new_coords[directions[j]] -= width
                yield tuple(new_coords)
                for k in range(j+1, len(directions)):
                    new_coords = list(coords)
                    new_coords[direction] -= width
                    new_coords[directions[j]] -= width
                    new_coords[directions[k]] -= width
                    yield tuple(new_coords)

    def _in_cut_electrode(self, coords: CoordsVar, simple_condition: typing.Callable[[CoordsVar], bool],
                       directions: typing.Optional[typing.Set]=None
                       ) -> int:
        """
        return cut the electrode from simple condition
        :param coords: current coordinates of the trap
        :param simple_condition: the function of the simple condition (etc z >= ...)
        :param directions: in which direction the electrode need to be cutted
           (for example the electrode of simple condition z >= 1 need to be leaded to 1 + delta >= z >= 1.

        :return: -1 for inside the trap, 0 for electrode, +1 for outside the trap
        """
        if not simple_condition(coords):
            # for example not `z >= z_0` means it is inside the trap
            return -1
        if directions is None:
            directions = self._standard_direction
        width = self.gridstepmm*self.electrode_width  # approximate width of the electrode
        for coords in self._gen_coords_for_test(coords, directions, width=width):
            # check in what coordinates we have electrode
            # if simple condition is:
            # .................|------------------------------------------
            # we generate for test coordinate just before condition: like
            #                 |
            #                 V
            # .................|------------------------------------------
            if not simple_condition(coords):
                # this means we are very near border. Closer to the border, than `width`. So, it is an electrode
                return 0
        # we are far away from border. it is not an electrode any more
        return 1

    @abstractmethod
    def _is_endcap_electrode_simple(self, coords: CoordsVar):
        """simple condidion for inner endcap electrode surface"""
        pass

    @abstractmethod
    def _is_other_electrode_simple(self, coords: CoordsVar):
        """simple condition for inner non-endcap electrode surface"""
        pass

    def _in_electrode_endcap(self, coords) -> int:
        """endcap electrode"""
        return self._in_cut_electrode(coords, self._is_endcap_electrode_simple, {2})

    def _in_other_electrode(self, coords) -> int:
        """other electrode"""
        if self.cylindrical_geometry:
            # we have the cylindrical symmetry, so no need for angle-coordinate
            directions = {0}
        else:
            # we don't have cylindical symmetry
            directions = {0, 1}
        return self._in_cut_electrode(coords, self._is_other_electrode_simple, directions)

    def is_endcap_electrode(self, coords: CoordsVar) -> bool:
        """is it endcap electrode"""
        if self._in_electrode_endcap(coords) == 0:
            # if in encap
            if self._in_other_electrode(coords) <= 0:
                # and inside the trap
                return True
        return False

    def is_other_electrode(self, coords: CoordsVar) -> bool:
        """is other electrode"""
        if self._in_other_electrode(coords) == 0:
            # if in other electrode
            if self._in_electrode_endcap(coords) <= 0:
                # and inside the trap
                return True
        return False

    # def show_this_pot(self, coords: CoordsVar):
    #     return self._in_other_electrode(coords) <= 0 and self._in_electrode_endcap(coords) <= 0
