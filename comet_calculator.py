import time

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import shutil
import os
from traps import abstract_trap
_A_20_COMPARABLE = 4195.527
_R_CLOUD = 2*10**-3
_R_EXCITATION = 6*10**-3
_Z_CLOUD = 4*2*10**-3
_2D_IMAGE_LOCATION = r"C:\Users\Anton.Lioznov\YandexDisk\work\Skoltech\2019\Marchall\images\averaged_phis"

def pure_cyclotron_motion(q, m, B):
    return B * q / m

def dY_2(R, Z):
    return R *0 + 1

def dY_4(R, Z):
    return 48 * Z**2 - 12 * R**2

def dY_6(R, Z):
    return 240 * Z**4 - 360 * Z**2 * R**2 + 30 * R**4

def magnetron_omega(q, m, B, A20, A40,  A60, r, z):
    omega_c_per_two = pure_cyclotron_motion(q, m, B) / 2
    # print(omega_c_per_two)
    return omega_c_per_two - np.sqrt(
        omega_c_per_two**2 - (q/m) * (
                A20 * dY_2(r, z)
                + A40 * dY_4(r, z)
                + A60 * dY_6(r, z)
        )
    )


def find_delta_omega(A20, A40, A60, d):
    m = 500
    q = 1
    q_e = 1.60217662 * 10**-19
    m_p = 1.6605e-27
    m *= m_p
    q *= q_e
    B = 7
    rs = np.linspace(_R_EXCITATION-_R_CLOUD, _R_EXCITATION+_R_CLOUD, 100) / d
    zs = np.linspace(-_Z_CLOUD, _Z_CLOUD, 100) / d
    Omega = np.zeros((100, 100))
    for i, r in enumerate(rs):
        for j, z in enumerate(zs):
            Omega[i, j] = magnetron_omega(q, m, B, A20, A40, A60, r, z) / d**2
    min_omega = np.min(Omega)
    max_omega = np.max(Omega)
    return min_omega, max_omega


def estimate_comet_time_formation(min_omega, max_omega):
    return 2*np.pi/(max_omega - min_omega)


def y_0(R, Z):
    return R * 0 + 1


def y_2(R, Z):
    return (
            +       Z**2
            - 0.5 * R**2
    )

def y_3(R, Z):
    return Z* (
        2 * Z**2
        - 3 * R**2
    )
def y_4(R, Z):
    return (
        + 8  * Z**4
        - 24 * Z**2 * R**2
        + 3         * R**4
    )


def y_6(R, Z):
    return (
        + 16  * Z**6
        - 120 * Z**4 * R**2
        + 90  * Z**2 * R**4
        - 5          * R**6
    )


def get_Y_coefs(Rs, Zs, Phi):
    Rs_flat = Rs.flatten()
    Zs_flat = Zs.flatten()
    # from https://stackoverflow.com/questions/33964913/equivalent-of-polyfit-for-a-2d-polynomial-in-python
    A = np.array([
        y_0(Rs_flat, Zs_flat),
        y_2(Rs_flat, Zs_flat),
        y_4(Rs_flat, Zs_flat),
        y_6(Rs_flat, Zs_flat),
    ]).T
    B = Phi.flatten()
    coeff, r, rank, s = np.linalg.lstsq(A, B)
    return coeff
    # A20, A30, A40, C = coeff
    # return A20, A30, A40, C


def _plot_1_line(coord, phi, phi_etalon, position, plt, axes=0, **kwargs):
    if axes == 1:
        coord = coord.T
        phi = phi.T
        phi_etalon = phi_etalon.T
    middle_ind = int(phi.shape[1]/2)-1
    # print(kwargs)
    plt.plot(coord[position, :]*1000, phi[position, :] + phi_etalon[position, middle_ind] - phi[position, middle_ind], **kwargs)


def _plot_2_lines(Rs, Zs, Phi, Phi20, position, color, axis: str, str_repr, plt):
    _axes = 0 if axis=="z" else 1
    coord = Rs if _axes == 0 else Zs
    _plot_1_line(coord, Phi, Phi, position, plt, _axes, linewidth=2, label=f"$\phi({axis}={str_repr})$", color=color)
    middle_ind = int(Phi.shape[1] / 2) - 1
    # c_coef = (position, middle_ind) if axis == 0 else (middle_ind, position)
    _plot_1_line(coord, Phi20, Phi, position, plt, _axes, linestyle="--", label=f"$approx(\phi({axis}={str_repr}))$", color=color)


def plot_graphic(Rs, Zs, Phi, Phi20, axis="z"):
    index_0 = int(Phi.shape[0] // 2)
    index_05 = int(index_0 + index_0*0.5)
    index_09 = int(index_0 + index_0*0.9)

    # lenght = 10*10**-3
    # ind = index_0 + int(lenght / abstract_trap.AVERAGED_AREA_LENGTH)
    # half_ind = int(Phi.shape[0] * 3 / 4) - 1
    fig = plt.figure()
    ax = plt.subplot(111)
    _plot_2_lines(Rs, Zs, Phi, Phi20, index_0, "blue", axis, "0", ax)
    norm = lambda axes: "z_0" if axes == "z" else "R"
    _plot_2_lines(Rs, Zs, Phi, Phi20, index_05, "orange", axis, f"0.5{norm(axis)}", ax)
    # slice0_9 = Rs.shape[0]
    # slice0_9 = int(slice0_9 / 2 + (slice0_9/2)*0.9)
    _plot_2_lines(Rs, Zs, Phi, Phi20, index_09, "yellow", axis, f"0.9{norm(axis)}", ax)
    second_axis = "r" if axis == "z" else "z"
    plt.title(f"$\phi({second_axis})$ on fixed {axis}",  fontsize=20)
    plt.xlabel(f"${second_axis}, mm$", fontsize=15)
    plt.ylabel("$\phi$, V", fontsize=15)
    # return ax
    handles, labels = ax.get_legend_handles_labels()
    # print(handles)
    # print(labels)
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    legend=ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), shadow=True, ncol=2, fontsize=15)
    # plt.show()
    fig.savefig(f"phi_comp_{axis}.png", bbox_extra_artists=(legend,),  bbox_inches='tight')

    # plt.savefig(f"phi_comp_{axis}.png")
    plt.cla()
    plt.clf()
    time.sleep(2)


def combine_copy_delete(trap: abstract_trap.AbstractPenningTrap, copy=True, delete=False, show=False):
    images = [Image.open(x) for x in [f"phi_comp_{ax}.png" for ax in ("r", "z")]]
    widths, heights = zip(*(i.size for i in images))
    width = int(sum(widths))
    height = max(heights)
    new_im = Image.new("RGB", (width, height), color="white")
    new_im.paste(images[0], (0, 0))
    new_im.paste(images[1], (new_im.size[0]-images[1].size[0], 0))
    new_im.save("phi_comp.png")
    if show:
        new_im.show()
    if copy:
        dist = f"{_2D_IMAGE_LOCATION}\\{trap.name}.png"
        shutil.copy("phi_comp.png", dist)
        print(f"trap image copied to {dist}")
    if delete:
        files_to_del = [
            f"{trap.cell_name}.pa#",
            f"{trap.cell_name}.pa0",
            "phi_comp.png",
            "phi_comp_r.png",
            "phi_comp_z.png"
        ]
        for v in trap._voltages:
            files_to_del.append(f"{trap.cell_name}.pa{v.value}")
        for f in files_to_del:
            os.remove(f)
        print("all temp files deleted")
