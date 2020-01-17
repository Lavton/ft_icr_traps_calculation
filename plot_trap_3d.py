from traps import abstract_trap
from typing import Set, Tuple, Optional, Callable
from tqdm import tqdm_notebook as tqdm
from queue import Queue
import numpy as np
from SIMION.PA import PA
import math
import time
from PIL import Image, ImageDraw, ImageFont
import shutil
from utils_for_trap import expand_trap, get_all_electrodes
from traps.abstract_trap import AbstractTrap
from plot_3d_trap_params import TrapVisParams
import os
_3D_IMAGE_LOCATION = r"C:\Users\Anton.Lioznov\YandexDisk\work\Skoltech\2019\Marchall\images\3D"


def create_temp_traps(trap: AbstractTrap, trap_params: Optional[TrapVisParams] = None):
    """
    creates expand trap for better visualization
    """
    trap.pa = PA(file=f"{trap.pa_filename}.pa#")
    expand_range = None
    if trap_params:
        expand_range = trap_params.expand_amount
    expand_trap(trap, expand_range)
    trap.pa = PA(file=f"{trap.pa_filename}_expanded.pa#")
    # leave_surface_only(trap)
    # trap.pa = PA(file=f"{trap.pa_file_name}_surface.pa#")
    return trap


def calc_and_plot_trap(trap: abstract_trap.AbstractTrap, trap_params: TrapVisParams, ipv, expanded=True):
    """creates 3D visualization in jupyter notebook"""
    e_types_colors = trap._voltages.EXCITATION.colors_for_3d()
    # what to visulize
    if expanded:
        trap.pa = PA(file=f"{trap.pa_filename}_expanded.pa#")
    else:
        trap.pa = PA(file=f"{trap.pa_filename}.pa#")
    # coordinates and types of electrodes
    coords, e_types = _get_coords_and_types(trap)
    # create 3D visualization
    ipv.figure()
    for c, e_type in zip(coords, e_types):
        # visualize as scatter
        ipv.scatter(c[:, 0], c[:, 1], c[:, 2], marker='box', size=0.5, color=e_types_colors[e_type])
    # the border
    ipv.xyzlim(-trap.trap_border.z*1.2, trap.trap_border.z*1.2)
    # ommit the axis
    ipv.style.use('minimal')
    ipv.show()
    # bad magic: ipv need some time to create the picture and only after it it will able to rotate the figure
    time.sleep(10)
    ipv.view(trap_params.view_th, trap_params.view_phi, trap_params.dist*trap.model_lenghts.x/trap.model_lenghts.z)
    # ipv.view(50, 25, 3.5 * trap.model_lenghts.x / trap.model_lenghts.z)
    # ipv.view(50, 25, 4)  # cubic
    # ipv.view(50, 25, 6*trap.model_lenghts.x/trap.model_lenghts.z)  # haperbolic
    # again same bad magic for saving fig
    time.sleep(10)
    if expanded:
        p_name = "expanded_trap.png"
    else:
        p_name = "original_trap.png"
    ipv.savefig(p_name)
    time.sleep(5)


def _get_coords_and_types(trap: abstract_trap.AbstractTrap):
    """get coordinates of the trap and it types"""
    electrodes, e_types = get_all_electrodes(trap, without_symmetry=False)
    coords = []
    for electrode in electrodes:
        coords.append(np.array(list(electrode)) * trap.gridstepmm)
    for i in range(len(e_types)):
        e_types[i] = int(e_types[i])
    return coords, e_types


def create_copy_delete(trap: abstract_trap.AbstractTrap, copy=True, delete=True, show=False):
    """postprocessing: modify picture, copy to distination"""
    create_figure(trap._voltages.EXCITATION.legend_for_3d(), show=show)
    time.sleep(1)
    if copy:
        dist = f"{_3D_IMAGE_LOCATION}\\{trap.name}.png"
        shutil.copy("trap.png", dist)
        print(f"trap image copied to {dist}")
    if delete:
        files_to_del = [
            f"{trap.pa_filename}.pa#",
            f"{trap.pa_filename}_expanded.pa#",
            # f"{trap.pa_file_name}_surface.pa#",
            "expanded_trap.png",
            "original_trap.png",
            "trap.png"
        ]
        for f in files_to_del:
            os.remove(f)
        print("all temp files deleted")


def create_figure(legend, show=False):
    """Postprocessing the image"""
    img: Image.Image = Image.open("expanded_trap.png")
    # use new size
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


