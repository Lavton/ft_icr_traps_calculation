from traps import abstract_trap
from typing import Set, Tuple
from tqdm import tqdm_notebook as tqdm
from queue import Queue
import numpy as np
from SIMION.PA import PA
import math
import time
from PIL import Image, ImageDraw, ImageFont
import shutil
import os
_3D_IMAGE_LOCATION = r"C:\Users\Anton.Lioznov\YandexDisk\work\Skoltech\2019\Marchall\images\3D"


def create_copy_delete(trap: abstract_trap.AbstractPenningTrap, copy=True, delete=True, show=False):
    create_figure(trap.legend_for_3d(), show=show)
    time.sleep(1)
    if copy:
        dist = f"{_3D_IMAGE_LOCATION}\\{trap.name}.png"
        shutil.copy("trap.png", dist)
        print(f"trap image copied to {dist}")
    if delete:
        files_to_del = [
            f"{trap.cell_name}.pa#",
            f"{trap.cell_name}_expanded.pa#",
            # f"{trap.pa_file_name}_surface.pa#",
            "expanded_trap.png",
            "original_trap.png",
            "trap.png"
        ]
        for f in files_to_del:
            os.remove(f)
        print("all temp files deleted")



def cart2spher(x,y,z):
    r = np.sqrt(x**2+y**2+z**2)
    theta = np.arctan2(np.sqrt(y**2+x**2), z)
    phi = np.arctan2(y, x)
    return r, theta, phi


def spher2cart(r, theta, phi):
    x = r*np.sin(theta)*np.cos(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)
    return x,y,z


def rotate_on_angles(coords, theta0, phi0):
    x = coords[:, 0]
    y = coords[:, 1]
    z = coords[:, 2]
    r, theta, phi = cart2spher(x, y, z)
    theta += theta0
    phi += phi0
    x, y, z = spher2cart(r, theta, phi)
    return np.vstack((x, y, z)).T


def _gen_near_coords(i, j, k, directions, delta=True):
    for i1 in directions:
        for j1 in directions:
            for k1 in directions:
                if delta:
                    yield i+i1, j+j1, k+k1
                else:
                    yield i*i1, j*j1, k*k1


def _dfs(i, j, k, trap: abstract_trap.AbstractTrap):
    visited_points = set()
    gray_points = set()
    queue = Queue()
    gray_points.add((i, j, k))
    queue.put((i, j, k))
    an_electrode = set()
    electrode_type = int(trap.pa.potential_real(abs(i), abs(j), abs(k)))
    while not queue.empty():
        i, j, k = queue.get()
        abs_neighbor = (abs(i), abs(j), abs(k))
        if abs_neighbor[0] >= trap.model_lenghts.x or abs_neighbor[1] >= trap.model_lenghts.y or abs_neighbor[2] >= trap.model_lenghts.z:
            continue
        if not trap.pa.electrode(*abs_neighbor):
            continue
        if (i, j, k) in visited_points:
            continue

        if int(trap.pa.potential_real(*abs_neighbor)) == electrode_type:
            an_electrode.add((i, j, k))
        else:
            continue

        visited_points.add((i, j, k))
        for neighbor in _gen_near_coords(i, j, k, (-1, 0, 1)):
            if neighbor not in visited_points and neighbor not in gray_points:
                gray_points.add(neighbor)
                queue.put(neighbor)
    return an_electrode, visited_points


def _calculate_mass_center(electrode: Set[Tuple[int, int, int]]):
    return np.array(list(electrode)).mean(axis=0)


def _delta_move(x_mc, y_mc, z_mc, r_delta=0.02):
    r, theta, phi = cart2spher(x_mc, y_mc, z_mc)
    r += r*r_delta
    x, y, z = spher2cart(r, theta, phi)
    return x-x_mc, y-y_mc, z-z_mc


def get_all_electrodes(trap: abstract_trap.AbstractTrap, without_simmetry=True):
    visited_points = set()
    electrodes = []
    e_types = []
    for k, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
        for i, x in enumerate(trap.grid.x):
            for j, y in enumerate(trap.grid.y):
                if trap.pa.electrode(i, j, k) and (i, j, k) not in visited_points:
                    e, v = _dfs(i, j, k, trap)
                    electrodes.append(e)
                    electrode_type = trap.pa.potential_real(i, j, k)
                    e_types.append(electrode_type)
                    visited_points = visited_points.union(v)
    if not without_simmetry:
        directions = np.array([-1, 1])
        for k_, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
            for i_, x in enumerate(trap.grid.x):
                for j_, y in enumerate(trap.grid.y):
                    for i, j, k in _gen_near_coords(i_, j_, k_, (-1, 1), delta=False):
                        if trap.pa.electrode(abs(i), abs(j), abs(k)) and (i, j, k) not in visited_points:
                            e, v = _dfs(i, j, k, trap)
                            electrodes.append(e)
                            electrode_type = trap.pa.potential_real(i, j, k)
                            e_types.append(electrode_type)
                            visited_points = visited_points.union(v)

    return electrodes, e_types


def expand_trap(trap: abstract_trap.AbstractPenningTrap):
    trap.load_adjusted_pa("#")
    electrodes, e_types = get_all_electrodes(trap)
    mass_centers = [_calculate_mass_center(electrode) for electrode in electrodes]
    r_shifts = []
    for e_type in e_types:
        if int(e_type) == 3:
            r_shifts.append(0.3) # compensated
            # r_shifts.append(0.1) # hyperbolic
        elif int(e_type) == 4:
            r_shifts.append(0.3)
        else:
            r_shifts.append(0.3)
    shifting = [_delta_move(*mc, r_delta=r_shift) for mc, r_shift in zip(mass_centers, r_shifts)]
    new_pa = trap.create_dump_pa()
    for sh, electrode, e_type in zip(shifting, electrodes, e_types):
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
    new_pa.save(f"{trap.cell_name}_expanded.pa#")


def _is_point_on_surface(i, j, k, trap: abstract_trap.AbstractPenningTrap):
    for i1, j1, k1 in _gen_near_coords(i, j, k, (-1,0, 1)):
        if not trap.pa.electrode(abs(i1), abs(j1), abs(k1)):
            return True
    return False


def leave_surface_only(trap: abstract_trap.AbstractPenningTrap):
    new_pa = trap.create_dump_pa()
    for k, z in tqdm(enumerate(trap.grid.z), total=trap.model_lenghts.z):
        for i, x in enumerate(trap.grid.x):
            for j, y in enumerate(trap.grid.y):
                if trap.pa.electrode(i, j, k):
                    if _is_point_on_surface(i, j, k, trap):
                        new_pa.point(i, j, k, 1, int(trap.pa.potential_real(i, j, k)))
    new_pa.save(f"{trap.cell_name}_surface.pa#")


def create_temp_traps(trap: abstract_trap.AbstractPenningTrap):
    trap.pa = PA(file=f"{trap.cell_name}.pa#")
    expand_trap(trap)
    trap.pa = PA(file=f"{trap.cell_name}_expanded.pa#")
    # leave_surface_only(trap)
    # trap.pa = PA(file=f"{trap.pa_file_name}_surface.pa#")
    return trap


def get_coords_end_types(trap: abstract_trap.AbstractPenningTrap):
    electrodes, e_types = get_all_electrodes(trap, without_simmetry=False)
    coords = []
    for electrode in electrodes:
        coords.append(np.array(list(electrode)) * trap.gridstepmm)
    for i in range(len(e_types)):
        e_types[i] = int(e_types[i])
    return coords, e_types


def calc_and_plot_trap(trap: abstract_trap.AbstractPenningTrap, ipv, e_types_colors, expanded=True):
    if expanded:
        trap.pa = PA(file=f"{trap.cell_name}_expanded.pa#")
    else:
        trap.pa = PA(file=f"{trap.cell_name}.pa#")
    coords, e_types = get_coords_end_types(trap)
    ipv.figure()
    for c, e_type in zip(coords, e_types):
        ipv.scatter(c[:, 0], c[:, 1], c[:, 2], marker='box', size=0.5, color=e_types_colors[e_type])
    ipv.xyzlim(-trap.cell_border.z*1.2, trap.cell_border.z*1.2)
    ipv.style.use('minimal')
    ipv.show()
    time.sleep(10)
    ipv.view(50, 25, 2.7*trap.model_lenghts.x/trap.model_lenghts.z)  # cylindar
    # ipv.view(50, 25, 3.5 * trap.model_lenghts.x / trap.model_lenghts.z)
    # ipv.view(50, 25, 4)  # cubic
    ipv.view(50, 25, 6*trap.model_lenghts.x/trap.model_lenghts.z)  # haperbolic
    time.sleep(10)
    if expanded:
        p_name = "expanded_trap.png"
    else:
        p_name = "original_trap.png"
    ipv.savefig(p_name)
    time.sleep(5)


def prepare_trap_to_pic(trap: abstract_trap.AbstractPenningTrap, expanded=True):
    if expanded:
        trap.pa = PA(file=f"{trap.cell_name}_expanded.pa#")
    else:
        trap.pa = PA(file=f"{trap.cell_name}.pa#")
    leave_surface_only(trap)
    trap.pa = PA(file=f"{trap.cell_name}_surface.pa#")
    return trap


def create_figure(legend, show=False):
    img: Image.Image = Image.open("expanded_trap.png")
    w, h = img.size
    new_h = 400
    img = img.crop((0, (h-new_h)/2, w, (h+new_h)/2))
    # NO legend and not expanded - we decide to left it to presentation
    # img2 = Image.open("original_trap.png")
    # img2 = img2.convert("RGBA")

    # font = ImageFont.truetype("arial.ttf", 20)
    # szes = img.size
    # k = 3
    # new_szes = (int(szes[0] / k), int(szes[1] / k))
    # d = ImageDraw.Draw(img)
    # d.rectangle(((0, 0), (250, len(legend) * 40 + 20)), fill=(220, 220, 220))
    # y = 10
    # for color, label in legend.items():
    #     d.rectangle(((10, y), (50, y + 30)), fill=color)
    #     d.text((65, y + 5), label, font=font, fill=(0, 0, 0))
    #     y += 40
    # img.paste(img2.resize(new_szes), (img.size[0] - new_szes[0], img.size[1] - new_szes[1]))
    # d.text((img.size[0] - 120, img.size[1] - new_szes[1] + 30), "original trap",
    #        font=ImageFont.truetype("arial.ttf", 15), fill=(0, 0, 0))
    if show:
        img.show()
    img.save("trap.png")