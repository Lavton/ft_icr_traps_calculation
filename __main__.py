import comet_calculator
import plot_trap_3d
from traps import cubic_trap, dhc_trap, dump_trap, cylindrical_trap, get_current_trap_3d, get_current_trap
from traps.abstract_trap import Coords
from SIMION.PA import PA
import numpy as np
import argparse
import logging
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s()-%(lineno)d:\t %(message)s')
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Создаёт визуализацию для сравнения ловушек")
    const_store = "store_const"

    parser.add_argument("--3d", action=const_store, const=1, help="Трёхмерная визуализация в Jupyter")
    parser.add_argument("--2d", action=const_store, const=1, help="Двумерная визуализация - поля и время образования кометы")
    args = parser.parse_args(["--2d"])
    if args.__getattribute__("3d"):
        logging.info("3D mode")
        trap = get_current_trap_3d()
        logging.info(trap.__class__)
        logging.info(trap.colors_for_3d())
        logging.info(trap.legend_for_3d())
        trap.generate_cell()
        trap = plot_trap_3d.create_temp_traps(trap)
        print("open Jupyter and run code.")

    if args.__getattribute__("2d"):
        logging.info("2d mode")
        trap = get_current_trap()
        logging.info(trap.__class__)
        trap.generate_cell()
        trap.refine_cell()
        trap.adjust_cell()
        trap.load_adjusted_pa()
        logging.info("trap created")
        Phi, Rs, Zs = trap.get_averaged_phi()
        A20, A30, A40, C = comet_calculator.get_Y_coefs(Rs, Zs, Phi)
        Phi20 = A20 * (Zs ** 2 - Rs ** 2 / 2)
        min_omega, max_omega = comet_calculator.find_delta_omega(A20, A30, A40)
        time_to_comet_formation = comet_calculator.estimate_comet_time_formation(min_omega, max_omega)
        print(f"!!!! TIME OF COMET FORMATION for trap '{trap.name}' = {time_to_comet_formation} s")
        comet_calculator.plot_graphic(Rs, Zs, Phi, Phi20, axis="z")
        comet_calculator.plot_graphic(Rs, Zs, Phi, Phi20, axis="r")
        comet_calculator.combine_copy_delete(trap)





