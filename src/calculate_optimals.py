import argparse
import sys
import numpy as np
from benchmark.print_format import read_in_csv_4D, create_csv

epsilon = 0.1

#identify utils corresponding to highest efficiency for each combination style + load level
def main(energies, utils_graphics, utils_mem, device):
    (num_graphics_levels, num_mem_levels, num_graphics_load_levels, num_mem_load_levels) = np.shape(energies)

    optimals = [[(-1,-1) for _ in range(num_mem_load_levels)] for _ in range(num_graphics_load_levels)]

    for mll in range(num_mem_load_levels):
        for gll in range(num_graphics_load_levels):
            curr_max_efficiency = sys.float_info.max
            curr_max_args = (-1, -1)
            for gdx in range(num_graphics_levels):
                for mdx in range(num_mem_levels):
                    energy = energies[gdx][mdx][gll][mll]
                    if (energy <= curr_max_efficiency) & (energy > epsilon):
                        curr_max_efficiency = energy
                        curr_max_args = (gdx, mdx)
            optimals[gll][mll] = curr_max_args

    #find lowest and highest load levels at which each graphics/mem frequency is optimal
    opts_g_low = [(num_graphics_levels + 1) for _ in range(num_graphics_levels)] 
    opts_g_high = [-1 for _ in range(num_graphics_levels)]
    opts_m_low = [(num_mem_levels + 1) for _ in range(num_mem_levels)] 
    opts_m_high = [-1 for _ in range(num_mem_levels)]
    for mll in range(num_graphics_load_levels):
        for gll in range(num_mem_load_levels):
            (opt_g, opt_m) = optimals[gll][mll]
            opts_g_low[opt_g] = min(opts_g_low[opt_g], gll)
            opts_g_high[opt_g] = max(opts_g_high[opt_g], gll)
            opts_m_low[opt_m] = min(opts_m_low[opt_m], mll)
            opts_m_high[opt_m] = max(opts_m_high[opt_m], mll)

    #extrapolate graphics load levels for values without a range
    #it is not necessary to check opts_g_low of immediate neighbours - from the previous algorithm both low and high 
    #values will be filled in iff there is at least one level for which the frequency is optimal. 
    repeat = True
    while (repeat):
        repeat = False
        for glx in range(num_graphics_levels):
            if opts_g_high[glx] == -1:
                if opts_g_high[max(glx - 1, 0)] != -1:
                    opt_low = min(max(opts_g_low[glx - 1] + 1, 0), num_graphics_load_levels - 1)
                    opt_high = min(max(opts_g_high[glx - 1] + 1, 0), num_graphics_load_levels - 1)
                    #perform sanity check
                    neighbours_above = [idx for idx in range(glx + 1, num_graphics_load_levels) if opts_g_high[idx] != -1]
                    if neighbours_above:
                        neighbour = min(neighbours_above)
                        opt_low = min(opt_low, opts_g_low[neighbour])
                        opt_high = min(opt_high, opts_g_high[neighbour])
                    opts_g_low[glx] = opt_low
                    opts_g_high[glx] = opt_high
                elif opts_g_high[min(glx + 1, num_graphics_levels)] != -1:
                    opt_low = min(max(opts_g_low[glx + 1] - 1, 0), num_graphics_load_levels - 1)
                    opt_high = min(max(opts_g_high[glx + 1] - 1, 0), num_graphics_load_levels - 1)
                    #perform sanity check
                    neighbours_below = [idx for idx in range(glx) if opts_g_high[idx] != -1]
                    if neighbours_below:
                        neighbour = max(neighbours_below)
                        opt_low = max(opt_low, opts_g_low[neighbour])
                        opt_high = max(opt_high, opts_g_high[neighbour])
                    opts_g_low[glx] = opt_low
                    opts_g_high[glx] = opt_high
                else:
                    repeat = True
    
    #repeat for memory
    repeat = True
    while (repeat):
        repeat = False
        for mlx in range(num_mem_levels):
            if opts_m_high[mlx] == -1:
                if opts_m_high[max(mlx - 1, 0)] != -1:
                    opt_low = min(max(opts_m_low[mlx - 1] + 1, 0), num_mem_load_levels - 1)
                    opt_high = min(max(opts_m_high[glx - 1] + 1, 0), num_mem_load_levels - 1)
                    #perform sanity check
                    neighbours_above = [idx for idx in range(mlx + 1, num_mem_load_levels) if opts_m_high[idx] != -1]
                    if neighbours_above:
                        neighbour = min(neighbours_above)
                        opt_low = min(opt_low, opts_m_low[neighbour])
                        opt_high = min(opt_high, opts_m_high[neighbour])
                    opts_m_low[mlx] = opt_low
                    opts_m_high[mlx] = opt_high
                elif opts_m_high[min(mlx + 1, num_mem_levels)] != -1:
                    opt_low = min(max(opts_m_low[mlx + 1] - 1, 0), num_mem_load_levels - 1)
                    opt_high = min(max(opts_m_high[mlx + 1] - 1, 0), num_mem_load_levels - 1)
                    #perform sanity check
                    neighbours_below = [idx for idx in range(mlx) if opts_m_high[idx] != -1]
                    if neighbours_below:
                        neighbour = max(neighbours_below)
                        opt_low = max(opt_low, opts_m_low[neighbour])
                        opt_high = max(opt_high, opts_m_high[neighbour])
                    opts_m_low[mlx] = opt_low
                    opts_m_high[mlx] = opt_high
                else:
                    #skip and set intention to revisit when immediate neighbours are filled in
                    repeat = True

    #find corresponding optimal utils for each pair of frequencies
    utils_up_g = [[-1 for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    utils_up_m = [[-1 for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    utils_low_g = [[-1 for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    utils_low_m = [[-1 for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]

    for glx in range(num_graphics_levels):
        for mlx in range(num_mem_levels):
            g_utils = utils_graphics[glx][mlx]
            m_utils = utils_mem[glx][mlx]
            utils_up_g[glx][mlx] = g_utils[opts_g_high[glx]][opts_m_high[mlx]]
            utils_up_m[glx][mlx] = m_utils[opts_g_high[glx]][opts_m_high[mlx]]
            utils_low_g[glx][mlx] = g_utils[opts_g_low[glx]][opts_m_low[mlx]]
            utils_low_m[glx][mlx] = m_utils[opts_g_low[glx]][opts_m_low[mlx]]
    
    #write to output files
    create_csv("utils_up_g_" + str(device), utils_up_g)
    create_csv("utils_up_m_" + str(device), utils_up_m)
    create_csv("utils_low_g_" + str(device), utils_low_g)
    create_csv("utils_low_m_" + str(device), utils_low_m)

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int, help="index of device to be profiled")
    parser.add_argument('-avg', '--average', action='store_true')
    args = parser.parse_args()

    #read in benchmark results
    device_str = str(args.device)
    energies = read_in_csv_4D("energies_" + device_str) if args.average else read_in_csv_4D("energies_" + device_str)
    utils_graphics = read_in_csv_4D("utils_graphics_average_" + device_str) if args.average else read_in_csv_4D("utils_graphics_" + device_str)
    utils_mem = read_in_csv_4D("utils_memory_average_" + device_str) if args.average else read_in_csv_4D("utils_memory_" + device_str)
    
    main(energies, utils_graphics, utils_mem, args.device)