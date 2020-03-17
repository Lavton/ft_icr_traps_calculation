from queue import Queue

import numpy as np
from tqdm import tqdm_notebook as tqdm
from typing import Tuple, List, Set, Optional, Callable
from SIMION.PA import PA
import math

from traps.abstract_trap import AbstractTrap, Coords

AVERAGED_AREA_LENGTH = 10 * 10 ** -3


def get_electrodes_slice(trap: AbstractTrap):
    electrodes_and_types = []
    for k, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
        for i, x in [(0, 0)]:
            for j, y in enumerate(trap.grid.y):
                # for each point in model space:
                if trap.pa.electrode(i, j, k):
                    electrodes_and_types.append(((x, y, z), trap.pa.potential_real(i, j, k)))
                    electrodes_and_types.append(((x, -y, z), trap.pa.potential_real(i, -j, k)))
                    electrodes_and_types.append(((x, y, -z), trap.pa.potential_real(i, j, -k)))
                    electrodes_and_types.append(((x, -y, -z), trap.pa.potential_real(i, -j, -k)))
    return electrodes_and_types


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


#  EXPAND AND SURFACE TRAP
def expand_trap(trap: AbstractTrap, expand_range: Optional[Callable[[int], Optional[float]]] = None):
    """
    Expand trap for better visualisation
    :param trap:
    :return:
    """
    trap.load_adjusted_pa("#")
    # get all electrodes and its types
    electrodes, e_types = get_all_electrodes(trap)
    # get mass centers of each electrode
    mass_centers = [_calculate_mass_center(electrode) for electrode in electrodes]
    # calculate the shifting of the electrode (0.3 is default)
    r_shifts = []
    for e_type in e_types:
        r_shift = None
        if expand_range:
            r_shift = expand_range(int(e_type))
        if r_shift is not None:
            r_shifts.append(r_shift)
        else:
            r_shifts.append(0.3)
    # find the dx, dy, dz from dr for all electrodes
    shifting = [_delta_move(*mc, r_delta=r_shift) for mc, r_shift in zip(mass_centers, r_shifts)]
    new_pa = trap.create_dump_pa()
    for sh, electrode, e_type in zip(shifting, electrodes, e_types):
        # make shifting
        if math.isnan(sh[0]):
            sh = (0, 0, 0)
        for i, j, k in tqdm(electrode):
            if i < 0 or j < 0 or k < 0:
                continue
            new_i = int(i+sh[0])
            new_j = int(j+sh[1])
            new_k = int(k+sh[2])
            try:
                new_pa.point(new_i, new_j, new_k, 1, int(e_type))
            except AssertionError:
                pass
    new_pa.save(f"{trap.pa_filename}_expanded.pa#")


def get_all_electrodes(trap: AbstractTrap, without_symmetry=True) -> Tuple[
    List[
        Set[Tuple[int, int, int]]
    ],
    List[float]
]:
    """
    without_symmetry - take into account xyz mirroring
    return all electrodes of the trap as a 2 lists:
    i-element of the first list is the set of 3-d points, i-element of the second is the electrode type
    """
    visited_points = set()
    electrodes = []
    e_types = []
    for k, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
        for i, x in enumerate(trap.grid.x):
            for j, y in enumerate(trap.grid.y):
                # for each point in model space:
                if trap.pa.electrode(i, j, k) and (i, j, k) not in visited_points:
                    # if this is an electrode point and we were not here yet
                    # use depth-first-search algorithm to visit all points of the electrode
                    e, v = _dfs(i, j, k, trap)
                    # add the result
                    visited_points = visited_points.union(v)
                    if len(e) > 20:
                        electrodes.append(e)
                        electrode_type = trap.pa.potential_real(i, j, k)
                        e_types.append(electrode_type)
    if not without_symmetry:
        # without symmetry also check the all other 7/8 of space
        for k_, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
            for i_, x in enumerate(trap.grid.x):
                for j_, y in enumerate(trap.grid.y):
                    # the next for unbending the 1/8 of space for the whole one
                    for i, j, k in _gen_near_coords(i_, j_, k_, (-1, 1), delta=False):
                        if trap.pa.electrode(abs(i), abs(j), abs(k)) and (i, j, k) not in visited_points:
                            e, v = _dfs(i, j, k, trap)
                            visited_points = visited_points.union(v)
                            if len(e) > 20:
                                electrodes.append(e)
                                electrode_type = trap.pa.potential_real(i, j, k)
                                e_types.append(electrode_type)

    return electrodes, e_types


def _dfs(i, j, k, trap: AbstractTrap):
    """Depth-first search algorithm.  Find the whole electrode based on 1 point"""
    visited_points = set()
    gray_points = set()
    queue = Queue()
    gray_points.add((i, j, k))
    queue.put((i, j, k))
    an_electrode = set()
    electrode_type = int(trap.pa.potential_real(abs(i), abs(j), abs(k)))
    while not queue.empty():
        # get new point to deal with
        i, j, k = queue.get()
        # because we have symmetry, use only abs of the points
        abs_neighbor = (abs(i), abs(j), abs(k))
        # if the point is outside the model space - do nothing
        if abs_neighbor[0] >= trap.model_lenghts.x or abs_neighbor[1] >= trap.model_lenghts.y or abs_neighbor[2] >= trap.model_lenghts.z:
            continue
        # if the point is not electode - do nothing
        if not trap.pa.electrode(*abs_neighbor):
            continue
        # if we already visit this point - do nothing
        if (i, j, k) in visited_points:
            continue
        # if it is a brand new point inside the electrode of the same type as the first one
        if int(trap.pa.potential_real(*abs_neighbor)) == electrode_type:
            # add this point to electrode points
            an_electrode.add((i, j, k))
        else:
            continue

        # and now we visit this point
        visited_points.add((i, j, k))
        for neighbor in _gen_near_coords(i, j, k, (-1, 0, 1)):
            # get all neighbors of the point
            if neighbor not in visited_points and neighbor not in gray_points:
                # if the neighbor is not visited and not in queue already, add it to queue
                gray_points.add(neighbor)
                queue.put(neighbor)
    return an_electrode, visited_points


def _gen_near_coords(i, j, k, directions, delta=True):
    """get coords near the given one"""
    for i1 in directions:
        for j1 in directions:
            for k1 in directions:
                if delta:
                    yield i+i1, j+j1, k+k1
                else:
                    yield i*i1, j*j1, k*k1


def _calculate_mass_center(electrode: Set[Tuple[int, int, int]]):
    """Calculate the mass center of the electrode"""
    return np.array(list(electrode)).mean(axis=0)


def _delta_move(x_mc, y_mc, z_mc, r_delta=0.02):
    """find dx, dy, dz to expand trap base on r_delta"""
    r, theta, phi = _cart2spher(x_mc, y_mc, z_mc)
    r += r*r_delta
    x, y, z = _spher2cart(r, theta, phi)
    return x-x_mc, y-y_mc, z-z_mc


def _cart2spher(x,y,z):
    r = np.sqrt(x**2+y**2+z**2)
    theta = np.arctan2(np.sqrt(y**2+x**2), z)
    phi = np.arctan2(y, x)
    return r, theta, phi


def _spher2cart(r, theta, phi):
    x = r*np.sin(theta)*np.cos(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)
    return x,y,z


# def _is_point_on_surface(i, j, k, trap: AbstractTrap):
#     for i1, j1, k1 in _gen_near_coords(i, j, k, (-1,0, 1)):
#         if not trap.pa.electrode(abs(i1), abs(j1), abs(k1)):
#             return True
#     return False
#
#
# def leave_surface_only(trap: AbstractTrap):
#     new_pa = trap.create_dump_pa()
#     for k, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
#         for i, x in enumerate(trap.grid.x):
#             for j, y in enumerate(trap.grid.y):
#                 if trap.pa.electrode(i, j, k):
#                     if _is_point_on_surface(i, j, k, trap):
#                         new_pa.point(i, j, k, 1, int(trap.pa.potential_real(i, j, k)))
#     new_pa.save(f"{trap.pa_filename}_surface.pa#")

