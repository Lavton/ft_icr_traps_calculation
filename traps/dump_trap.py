from traps.abstract_trap import AbstractTrap, Coords, CoordsVar


class DumpTrap(AbstractTrap):
    def is_electrode(self, coords: CoordsVar):
        return True

    def get_electrode_type(self, coords: CoordsVar):
        return 1


if __name__ == "__main__":
    dump_trap = DumpTrap(Coords(4, 4, 4))
    dump_trap.generate_cell()
    print("created")