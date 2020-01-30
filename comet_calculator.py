"""
module for calculate the spherical harmonic coefficients as well as time of comet formation
"""
import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import shutil
import os
from traps import abstract_trap
_A_20_COMPARABLE = 4320.840
_R_CLOUD = 2*10**-3
_R_EXCITATION = 6*10**-3
_Z_CLOUD = 4*2*10**-3
_2D_IMAGE_LOCATION = r"C:\Users\Anton.Lioznov\YandexDisk\work\Skoltech\2019\Marchall\images\averaged_phis"

#    CALCULATION OF COMET FORMATION TIME & SPHERICAL HARMONICS COEFFICIENTS
def get_Y_coefs(Rs, Zs, Phi, d):
    """calculate the coefficients of spherical harmonics Y00, Y20, Y40, Y60 """
    Rs_flat = Rs.flatten() / d
    Zs_flat = Zs.flatten() / d
    # from https://stackoverflow.com/questions/33964913/equivalent-of-polyfit-for-a-2d-polynomial-in-python
    A = np.array([
        _y_0(Rs_flat, Zs_flat),
        _y_2(Rs_flat, Zs_flat),
        _y_4(Rs_flat, Zs_flat),
        _y_6(Rs_flat, Zs_flat),
    ]).T
    B = Phi.flatten()
    coeff, r, rank, s = np.linalg.lstsq(A, B)
    return tuple(coeff)


def print_coeffs(coeffs):
    printable = ["{:.1e}".format(c) for c in coeffs[1:]]
    result = f"$A_{{20}} = {printable[0]}$, $A_{{40}} = {printable[1]}$, $A_{{60}} = {printable[2]}$"
    print(result)


def find_delta_omega(A00, A20, A40, A60, d):
    """find the min and max magnetron frequency in the area of ion cloud"""
    m = 500  # mass
    q = 1  # charge
    q_e = 1.60217662 * 10**-19  # charge of electron, Kl
    m_p = 1.6605e-27  # absolute mass of proton, kg
    m *= m_p
    q *= q_e
    B = 7  # magnetic field in T
    # the area where ion cloud in rotatin
    rs = np.linspace(_R_EXCITATION-_R_CLOUD, _R_EXCITATION+_R_CLOUD, 100) / d
    zs = np.linspace(-_Z_CLOUD, _Z_CLOUD, 100) / d
    # find magnetron frequency at each r, z
    Omega = np.zeros((100, 100))
    for i, r in enumerate(rs):
        for j, z in enumerate(zs):
            Omega[i, j] = _reduced_cyclotron_freq(q, m, B, A20, A40, A60, r, z) / d ** 2
    # find min and max frequency
    min_omega = np.min(Omega)
    max_omega = np.max(Omega)
    return min_omega, max_omega


def _pure_cyclotron_freq(q, m, B):
    """pure cyclotron frequency"""
    return B * q / m


def _reduced_cyclotron_freq(q, m, B, A20, A40, A60, r, z):
    """estimate the magnetron frequency"""
    omega_c_per_two = _pure_cyclotron_freq(q, m, B) / 2
    # print("test")
    return omega_c_per_two + np.sqrt(
        omega_c_per_two**2 - (q/m) * (
                A20 * _dY_2(r, z)
                + A40 * _dY_4(r, z)
                + A60 * _dY_6(r, z)
        )
    )


def estimate_comet_time_formation(min_omega, max_omega):
    return 2*np.pi/(max_omega - min_omega)


#           PLOT AVERAGE POTENTIAL
def plot_graphic(Rs, Zs, Phi, Phi20, axis="z"):
    """plotting the averaged potential"""
    index_0 = int(Phi.shape[0] // 2)
    index_05 = int(index_0 + index_0*0.5)
    index_09 = int(index_0 + index_0*0.9)

    fig = plt.figure()
    ax = plt.subplot(111)
    _plot_2_lines(Rs, Zs, Phi, Phi20, index_0, "blue", axis, "0", ax)
    norm = lambda axes: "z_0" if axes == "z" else "R"
    _plot_2_lines(Rs, Zs, Phi, Phi20, index_05, "orange", axis, f"0.5{norm(axis)}", ax)
    _plot_2_lines(Rs, Zs, Phi, Phi20, index_09, "yellow", axis, f"0.9{norm(axis)}", ax)
    second_axis = "r" if axis == "z" else "z"
    plt.title(f"$\phi({second_axis})$ on fixed {axis}",  fontsize=20)
    plt.xlabel(f"${second_axis}, mm$", fontsize=15)
    plt.ylabel("$\phi$, V", fontsize=15)
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    legend=ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), shadow=True, ncol=2, fontsize=15)
    fig.savefig(f"phi_comp_{axis}.png", bbox_extra_artists=(legend,),  bbox_inches='tight')

    plt.cla()
    plt.clf()
    time.sleep(2)


def _plot_1_line(coord, phi, phi_etalon, position, plt, axes=0, **kwargs):
    if axes == 1:
        coord = coord.T
        phi = phi.T
        phi_etalon = phi_etalon.T
    middle_ind = int(phi.shape[1]/2)-1
    plt.plot(coord[position, :]*1000, phi[position, :] + phi_etalon[position, middle_ind] - phi[position, middle_ind], **kwargs)


def _plot_2_lines(Rs, Zs, Phi, Phi20, position, color, axis: str, str_repr, plt):
    _axes = 0 if axis=="z" else 1
    coord = Rs if _axes == 0 else Zs
    _plot_1_line(coord, Phi, Phi, position, plt, _axes, linewidth=2, label=f"$\phi({axis}={str_repr})$", color=color)
    _plot_1_line(coord, Phi20, Phi, position, plt, _axes, linestyle="--", label=f"$approx(\phi({axis}={str_repr}))$", color=color)


def plot_contour(Rs, Zs, Phi, trap, number=10, mode="half"):
    colorinterpolation = 200
    colourMap = plt.cm.plasma
    l = Rs.shape[0] // 2 + 1
    if mode=="half":
        CS = plt.contourf(Zs[:l, :], Rs[:l, :], Phi[:l, :], colorinterpolation, cmap=colourMap)
    if mode=="full":
        CS = plt.contourf(Zs[:, :], Rs[:, :], Phi[:, :], colorinterpolation, cmap=colourMap)
    if mode=="quarter":
        CS = plt.contourf(Zs[:l, :l], Rs[:l, :l], Phi[:l, :l], colorinterpolation, cmap=colourMap)
    levels = np.linspace(Phi.min(), Phi.max(), number)
    modified_l = np.exp((levels / levels[-1])[::-1] * 2) / np.exp(2)
    colors = [(l, l, l) for l in modified_l]
    CS2 = plt.contour(CS, levels=levels, colors=colors)
    cbar = plt.colorbar(CS)
    cbar.add_lines(CS2)
    plt.savefig("contour.png")
    shutil.copy("contour.png", f"{_2D_IMAGE_LOCATION}\\{trap.name}_contour.png")
    shutil.copy("contour.png", f"{_2D_IMAGE_LOCATION}\\{trap.name}_contour_{mode}.png")


def combine_copy_delete(trap: abstract_trap.AbstractTrap, copy=True, delete=False, show=False):
    """combine and save 2 graphics"""
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
            f"{trap.pa_filename}.pa#",
            f"{trap.pa_filename}.pa0",
            "phi_comp.png",
            "phi_comp_r.png",
            "phi_comp_z.png"
        ]
        for v in trap._voltages:
            files_to_del.append(f"{trap.pa_filename}.pa{v.value}")
        for f in files_to_del:
            os.remove(f)
        print("all temp files deleted")


# spherical harmonics and its d/dR
def _y_0(R, Z):
    return R * 0 + 1


def _y_2(R, Z):
    return (
            +       Z**2
            - 0.5 * R**2
    )


def _y_3(R, Z):
    return Z* (
            2 * Z**2
            - 3 * R**2
    )


def _y_4(R, Z):
    return (
            + 8  * Z**4
            - 24 * Z**2 * R**2
            + 3         * R**4
    )


def _y_6(R, Z):
    return (
            + 16  * Z**6
            - 120 * Z**4 * R**2
            + 90  * Z**2 * R**4
            - 5          * R**6
    )


def _dY_2(R, Z):
    return R *0 + 1


def _dY_4(R, Z):
    return 48 * Z**2 - 12 * R**2


def _dY_6(R, Z):
    return 240 * Z**4 - 360 * Z**2 * R**2 + 30 * R**4
