from traps import cubic_trap, dhc_trap, dump_trap, cylindrical_trap
from traps.abstract_trap import Coords
from SIMION.PA import PA

if __name__ == "__main__":
    # trap = dump_trap.DumpTrap(Coords(1, 1, 1))
    # trap = cubic_trap.CubicTrap(20*10**-3)
    trap = cylindrical_trap.CylindricalTrap(a=20*10**-3, z0=20*10**-3)
    # trap = dhc_trap.DHCTrap(
    #     a=30*10**-3,
    #     z0=2*30*10**-3,
    #     beta=0.9
    # )
    trap.generate_cell()
    # trap.refine_cell()
    # trap.adjust_cell()
    # trap.load_adjusted_pa()
    # trap.get_averaged_phi()
    # trap.plot_3D_electrodes()
    print("done")

