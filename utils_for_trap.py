import numpy as np
from tqdm import tqdm_notebook as tqdm
from typing import Tuple

from traps.abstract_trap import AbstractTrap, Coords

AVERAGED_AREA_LENGTH = 10 * 10 ** -3


def get_averaged_phi(trap: AbstractTrap, r_pts=50, z_pts=50, max_r=AVERAGED_AREA_LENGTH, max_z=AVERAGED_AREA_LENGTH):
    """return 2D numpy array of electric potential from .pa file, averaged over angle in cylindical coordinate system"""
    # grid points of averaging
    rs = np.linspace(0, 1, r_pts)
    zs = np.linspace(0, 1, z_pts)
    Rs, Zs = np.meshgrid(rs, zs)
    Phi = np.zeros_like(Rs)
    for i in tqdm(range(Rs.shape[0])):
        for j in range(Rs.shape[1]):
            # calculate the 1 point - average over angle
            Phi[i, j] = _get_averaged_phi_point(trap, Rs[i, j], Zs[i, j], max_r, max_z)
    return _unbend_phi2D(Phi, Rs * max_r, Zs * max_z)


#           AVERAGING POTENTIAL
def _get_averaged_phi_point(trap: AbstractTrap, rfrac, zfrac, max_r, max_z, num_th=0):
    """
    average the electric potential for current r, z
    :param trap: the trap class
    :param zfrac: the fraction of z from 0 to 1
    :param rfrac: the fraction of r from 0 to 1
    :param max_r: what rfrac=1 is equ to
    :param max_z: what zfrac=1 is equ to
    :param num_th: the number of averaging points (may use default pts*pi/2)
    :return: the mean value of potential
    """
    if not num_th:
        num_th = int(trap.pts*np.pi/2)
    z = zfrac * max_z
    r = rfrac * max_r
    return np.mean(np.array(
        [_numerical_phi_cylindrical(trap, z, r, theta) for theta in np.linspace(0, np.pi/2, num_th)]
    ))


def _numerical_phi_cylindrical(trap, z, r, theta):
    """find phi in cylindrical coordinate"""
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return _numerical_phi_cartesian(trap, Coords(x, y, z))


def _numerical_phi_cartesian(trap: AbstractTrap, coords: Coords[float]):
    """return the electric potential from PA file in given point in space using the cartesian coords"""
    # the point in space may not lay on grid. We need to average it
    # 1) calculate the index of point (float, it will be averaged near closed grid
    indexes_float = _get_float_ind(coords, trap.gridstepmm)
    i = int(np.floor(indexes_float.x))
    j = int(np.floor(indexes_float.y))
    k = int(np.floor(indexes_float.z))
    # return self.pa.potential_real(i, j, k) # for fast creating
    # find potential in points near by
    alpha = indexes_float.x - i
    beta = indexes_float.y - j
    gamma = indexes_float.z - k
    p000 = trap.pa.potential_real(x=i, y=j, z=k)
    p001 = trap.pa.potential_real(x=i, y=j, z=k + 1)
    p010 = trap.pa.potential_real(x=i, y=j + 1, z=k)
    p011 = trap.pa.potential_real(x=i, y=j + 1, z=k + 1)
    p100 = trap.pa.potential_real(x=i + 1, y=j, z=k)
    p101 = trap.pa.potential_real(x=i + 1, y=j, z=k + 1)
    p110 = trap.pa.potential_real(x=i + 1, y=j + 1, z=k)
    p111 = trap.pa.potential_real(x=i + 1, y=j + 1, z=k + 1)
    # average with coefficients
    return (
            +(alpha) * (beta) * (gamma) * p111
            + (alpha) * (1 - beta) * (gamma) * p101
            + (alpha) * (beta) * (1 - gamma) * p110
            + (alpha) * (1 - beta) * (1 - gamma) * p100
            + (1 - alpha) * (beta) * (gamma) * p011
            + (1 - alpha) * (1 - beta) * (gamma) * p001
            + (1 - alpha) * (beta) * (1 - gamma) * p010
            + (1 - alpha) * (1 - beta) * (1 - gamma) * p000
    )


def _get_float_ind(coords: Coords[float], gridstepmm: float) -> Coords[float]:
    """get float index of grid"""
    return Coords(
        x=coords.x / gridstepmm,
        y=coords.y / gridstepmm,
        z=coords.z / gridstepmm
    )
#          /AVERAGING POTENTIAL

def _unbend_phi2D(Phi, Rs, Zs) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """originally we have xyz symmetry and only 1/8 of the full space. Here we unbend r,z for r,-z, -r,z, -r,-z"""
    Phi_th = np.vstack((Phi[-2::-1, :], Phi))
    Phi_th = np.hstack((Phi_th[:, -2::-1], Phi_th))
    Rs_th = np.vstack((Rs[-2::-1, :], Rs))
    Rs_th = np.hstack((-Rs_th[:, -2::-1], Rs_th))
    Zs_th = np.vstack((-Zs[-2::-1, :], Zs))
    Zs_th = np.hstack((Zs_th[:, -2::-1], Zs_th))
    return Phi_th, Rs_th, Zs_th
