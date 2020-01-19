# from view_ipvolume.trap_view import CubicTrapView
from plot_3d_trap_params import TrapVisParams
from traps import hyperbolic_trap, hyperbolic_compensated, cuboid_trap, cubic_trap, cylindrical_trap
from traps import closed_compesated, open_compensated
# from traps import hyperbolic_compensated


def get_current_trap_3d():
    R = 20 * (10 ** -3)
    # trap, params = hyperbolic_trap.HyperbolicTrap(a=R, z0=R/1.414, pts=250, r_max=2*R), TrapVisParams(dist=5)
    # trap, params = hyperbolic_compensated.HyperbolicCompensatedTrap(a=R, z0=R / 1.16, rc=2 * R, r_max=2 * R, pts=200), TrapVisParams(dist=5, expand_amount=lambda v: 0.4 if v==3 else 0.2 if v==4 else None)
    # trap, params = cuboid_trap.CuboidTrap(76.2*10**-3, 25.4*10**-3, 24.4*10**-3, pts=300), TrapVisParams(dist=1.8)
    # trap, params = cubic_trap.CubicTrap(R, pts=100), TrapVisParams(dist=3)
    # trap, params = cylindrical_trap.CylindricalTrap(a=R, z0=R, pts=110), TrapVisParams(dist=2.5)
    # trap, params = closed_compesated.ClosedCompesatedCylindricalTrap(a=1.16*R, z0=R, dzc=0.3*R, pts=150), TrapVisParams(dist=2.5, expand_amount=lambda v: 0.4 if v==3 else 0.2 if v==4 else None)
    trap, params = open_compensated.OpenCompensatedCylindricalTrap(a=1.0239 * R, z0=R, dzc=0.8351 * R, ze=4.327 * R, pts=120), TrapVisParams(dist=50)
    # trap = dhc_trap.DHCTrap(
    #     a=30*10**-3,
    #     z0=2*30*10**-3,
    #     beta=0.9, pts=100
    # )
    return trap, params


def get_current_trap():
    R = (25.4*10**-3)/2
    # trap = hyperbolic_trap.HyperbolicTrap(a=R, z0=R/1.414, pts=150, r_max=2*R)
    # trap = hyperbolic_compensated.HyperbolicCompensatedTrap(a=R, z0=R/1.16, pts=250, r_max=2*R, rc=2*R)
    # trap = cuboid_trap.CuboidTrap(76.2*10**-3/2, 25.4*10**-3/2, 24.4*10**-3/2, pts=150*3)
    # trap = cubic_trap.CubicTrap(R, pts=200)
    # trap = cylindrical_trap.CylindricalTrap(a=R, z0=R, pts=200)
    # trap = closed_compesated.ClosedCompesatedCylindricalTrap(a=1.16*R, z0=R, dzc=0.3*R, pts=200)
    trap = open_compensated.OpenCompensatedCylindricalTrap(a=1.0239*R, z0=R, dzc=0.8351*R, ze=4.327*R, pts=220)
    # trap = dhc_trap.DHCTrap(
    #     a=R,
    #     z0=2*R,
    #     beta=0.9, pts=150
    # )
    return trap

