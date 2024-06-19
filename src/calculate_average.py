
import numpy as np
import glob
import argparse
import os
from functools import reduce
from print_format import read_in_csv_4D, create_csv_4D, create_latex, time_created, combine

def main(device):
        
        #element-wise average of a list of arrays
        def average_of(arrs):
            return ((reduce(lambda x, y: x + y, [np.array(arr, dtype=(np.float64)) for arr in arrs])) / len(arrs))

        #locate all measurements of utilisation and energy consumption
        utils_graphics_paths = glob.glob("results/utils_graphics_" + str(device) + "*.csv")
        utils_mem_paths = glob.glob("results/utils_mem_" + str(device) + "*.csv")
        energy_paths = glob.glob("results/energies_" + str(device) + "*.csv")

        #read in utilisations and energy consumptions
        all_utils_graphics = [read_in_csv_4D(u[:-4]) for u in utils_graphics_paths]
        all_utils_mem = [read_in_csv_4D(u[:-4]) for u in utils_mem_paths]
        all_energy = [read_in_csv_4D(e[:-4]) for e in energy_paths]

        #calculate averages
        avg_utils_graphics = average_of(all_utils_graphics)
        avg_utils_mem = average_of(all_utils_mem)
        avg_utils_combined = combine(avg_utils_graphics, avg_utils_mem)
        avg_energy = average_of(all_energy).tolist()
        
        #replace averages
        graphics_prefix = "results/utils_average_graphics_" + str(device)
        memory_prefix = "results/utils_average_memory_" + str(device)
        utils_prefix = "results/utils_average_" + str(device)
        energy_prefix = "results/energy_average_" + str(device)

        if os.path.exists(graphics_prefix + ".csv"):  
            os.remove(graphics_prefix + ".csv")
        if os.path.exists(memory_prefix + ".csv"):  
            os.remove(memory_prefix + ".csv")
        if os.path.exists(energy_prefix + ".csv"):  
            os.remove(energy_prefix + ".csv")
        if os.path.exists(energy_prefix + ".txt"):  
            os.remove(energy_prefix + ".txt")
        if os.path.exists(utils_prefix + ".txt"):  
            os.remove(utils_prefix + ".txt")
        
        create_csv_4D(graphics_prefix, avg_utils_graphics.tolist())
        create_csv_4D(memory_prefix, avg_utils_mem.tolist())
        create_csv_4D(energy_prefix, avg_energy)
        create_latex(utils_prefix, avg_utils_combined, device)
        create_latex(energy_prefix, avg_energy, device)

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int, help="index of device to be profiled")
    args = parser.parse_args()
    main(args.device)

