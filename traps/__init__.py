
from traps import cubic_trap #, cylindrical_trap, dhc_trap, cuboid_trap, closed_compesated, hyperbolic_trap
# from traps import hyperbolic_compensated


def get_current_trap_3d():
    R = 20 * (10 ** -3)
    trap = cubic_trap.CubicTrap(20 * 10 ** -3, pts=100)
    # trap = cylindrical_trap.CylindricalTrap(a=20 * 10 ** -3, z0=20 * 10 ** -3, pts=110)
    # trap = hyperbolic_compensated.HyperbolicCompensatedTrap(a=R, z0=R / 1.16, rc=2 * R, r_max=2 * R, pts=150)
    # trap = cuboid_trap.CuboidTrap(76.2*10**-3, 25.4*10**-3, 24.4*10**-3, pts=300)
    # trap = closed_compesated.ClosedCompesatedCylindricalTrap(20 * 10**-3, pts=150)
    # trap = hyperbolic_trap.HyperbolicTrap(a=20*10**-3, z0=20*10**-3/1.414, pts=300)
    # trap = dhc_trap.DHCTrap(
    #     a=30*10**-3,
    #     z0=2*30*10**-3,
    #     beta=0.9, pts=100
    # )
    return trap


def get_current_trap():
    R = (25.4*10**-3)/2
    trap = cubic_trap.CubicTrap(R, pts=200)
    # trap = cuboid_trap.CuboidTrap(76.2*10**-3/2, 25.4*10**-3/2, 24.4*10**-3/2, pts=150*3)
    # trap = hyperbolic_compensated.HyperbolicCompensatedTrap(a=R, z0=R/1.16, rc=2*R, r_max=2*R, pts=150)
    # trap = cylindrical_trap.CylindricalTrap(a=R, z0=2*R, pts=200)
    # trap = hyperbolic_trap.HyperbolicTrap(a=R, z0=R/1.414, pts=250)
    # trap = closed_compesated.ClosedCompesatedCylindricalTrap(R, pts=200)
    # trap = dhc_trap.DHCTrap(
    #     a=R,
    #     z0=2*R,
    #     beta=0.9, pts=150
    # )
    return trap

