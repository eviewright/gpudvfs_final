
import numpy as np
import glob
import argparse
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
        
        #write out averages
        create_csv_4D("results/utils_average_graphics" + time_created(), avg_utils_graphics.tolist())
        create_csv_4D("results/utils_average_mem" + time_created(), avg_utils_mem.tolist())
        create_csv_4D("results/energy_average" + time_created(), avg_energy)
        create_latex("results/utils_average" + time_created(), avg_utils_combined, device)
        create_latex("results/energy_average" + time_created(), avg_energy, device)

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int, help="index of device to be profiled")
    args = parser.parse_args()
    main(args.device)

