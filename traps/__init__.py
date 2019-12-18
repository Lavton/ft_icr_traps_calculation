
from traps import cubic_trap, cylindrical_trap, dhc_trap


def get_current_trap_3d():
    # trap = cubic_trap.CubicTrap(20 * 10 ** -3, pts=100)
    # trap = cylindrical_trap.CylindricalTrap(a=20 * 10 ** -3, z0=20 * 10 ** -3, pts=110)
    trap = dhc_trap.DHCTrap(
        a=30*10**-3,
        z0=2*30*10**-3,
        beta=0.9, pts=100
    )
    return trap


def get_current_trap():
    R = 25.4*10**-3
    # trap = cubic_trap.CubicTrap(R, pts=200)
    # trap = cylindrical_trap.CylindricalTrap(a=R, z0=R, pts=200)
    trap = dhc_trap.DHCTrap(
        a=R,
        z0=2*R,
        beta=0.9, pts=150
    )
    return trap

