# from view_ipvolume.trap_view import CubicTrapView
from plot_3d_trap_params import TrapVisParams
from traps import hyperbolic_trap, hyperbolic_compensated, cuboid_trap, cubic_trap, cylindrical_trap
from traps import closed_compesated, open_compensated, dhc_trap

from traps import tolmachov_trap, brustkern_trap, infinity_cell, trapping_ring, pseudo_pot_trap


def get_current_trap_3d():
    R = 20 * (10 ** -3)
    # trap, params = hyperbolic_trap.HyperbolicTrap(a=R, z0=R/1.414, pts=250, r_max=2*R), TrapVisParams(dist=5)
    # trap, params = hyperbolic_compensated.HyperbolicCompensatedTrap(a=R, z0=R / 1.16, rc=2 * R, r_max=2 * R, pts=200), TrapVisParams(dist=5, expand_amount=lambda v: 0.4 if v==3 else 0.2 if v==4 else None)
    # trap, params = cuboid_trap.CuboidTrap(76.2*10**-3, 25.4*10**-3, 24.4*10**-3, pts=300), TrapVisParams(dist=1.8)
    # trap, params = cubic_trap.CubicTrap(R, pts=100), TrapVisParams(dist=3)
    # trap, params = cylindrical_trap.CylindricalTrap(a=R, z0=R, pts=110), TrapVisParams(dist=2.5)
    # trap, params = closed_compesated.ClosedCompesatedCylindricalTrap(a=1.16*R, z0=R, dzc=0.3*R, pts=150), TrapVisParams(dist=2.5, expand_amount=lambda v: 0.4 if v==3 else 0.2 if v==4 else None)
    # trap, params = open_compensated.OpenCompensatedCylindricalTrap(a=1.0239 * R, z0=R, dzc=0.8351 * R, ze=4.327 * R, pts=120), TrapVisParams(dist=50)
    # trap, params = dhc_trap.DHCTrap(a=R, z0=2*R, beta=0.9, pts=200), TrapVisParams()

    # trap, params = tolmachov_trap.TolmachovTrap(a=R, pts=100), TrapVisParams(dist=15)
    # trap, params = brustkern_trap.BrustkernTrap(a=R, pts=100), TrapVisParams(dist=12)
    # trap, params = infinity_cell.InfinityCell(a=R, z0=R, pts=100), TrapVisParams(dist=2.5)
    # trap, params = trapping_ring.TrappingRingTrap(a=R, pts=100), TrapVisParams(dist=2.5)
    trap, params = pseudo_pot_trap.PseudoPotentialTrap(a=R, z0=R, wire_num=15, pts=100), TrapVisParams(dist=2.5)
    return trap, params


def get_current_trap():
    R = (25.4*10**-3)/2
    # trap = hyperbolic_trap.HyperbolicTrap(a=R, z0=R/1.414, pts=150, r_max=2*R)
    # trap = hyperbolic_compensated.HyperbolicCompensatedTrap(a=R, z0=R/1.16, pts=250, r_max=2*R, rc=2*R)
    # trap = cuboid_trap.CuboidTrap(76.2*10**-3/2, 25.4*10**-3/2, 24.4*10**-3/2, pts=150*3)
    # trap = cubic_trap.CubicTrap(R, pts=200)
    # trap = cylindrical_trap.CylindricalTrap(a=R, z0=R, pts=200)
    # trap = closed_compesated.ClosedCompesatedCylindricalTrap(a=1.16*R, z0=R, dzc=0.3*R, pts=200)
    # trap = open_compensated.OpenCompensatedCylindricalTrap(a=1.0239*R, z0=R, dzc=0.8351*R, ze=4.327*R, pts=220)
    # trap = dhc_trap.DHCTrap(a=R, z0=2*R, beta=0.9, pts=200)
    # trap = tolmachov_trap.TolmachovTrap(a=R, pts=200)
    # trap = brustkern_trap.BrustkernTrap(a=R, pts=100)
    # trap = infinity_cell.InfinityCell(a=R, z0=R, pts=150)
    trap = trapping_ring.TrappingRingTrap(a=R, pts=150)
    return trap

