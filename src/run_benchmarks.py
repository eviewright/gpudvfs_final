import argparse
import os
import time as tt
import numpy as np
import cupy as cp
import pynvml
from datetime import date
from zeus.monitor import power as zeus_power
from benchmark_threads import DenseMatMulThread, DenseTransposeThread
from print_format import *
from cfg import *

# constants
gpu_clock = 0
memory_clock = 2
update_period = 0.1
reset_period = 3
num_streams = 1
elem_size = 8

def run_benchmark():
    
    def measure_benchmark(mt, cpt):
      gpu_util = 0
      mem_util = 0
      power = 0
      it = 0
      mt.start()
      cpt.start()
      start_time = tt.time()
      tt.sleep(1)
      while mt.is_alive() | cpt.is_alive():
          utils = pynvml.nvmlDeviceGetUtilizationRates(handle) 
          gpu_util += utils.gpu 
          mem_util += utils.memory 
          power += pm.get_power()[device_index]
          it += 1
          tt.sleep(update_period)
      elapsed_time = tt.time() - start_time
      it = max(it, 1)
      return gpu_util/it, mem_util/it, (power/(it * update_period)) * elapsed_time, elapsed_time
    
    utilisations_graphics = [[[[-1.0 for _ in range(num_mem_load_levels)] for _ in range(num_graphics_load_levels)] for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    utilisations_mem = [[[[-1.0 for _ in range(num_mem_load_levels)] for _ in range(num_graphics_load_levels)] for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    energies = [[[[-1.0 for _ in range(num_mem_load_levels)] for _ in range(num_graphics_load_levels)] for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    execution_times = [[[[-1.0 for _ in range(num_mem_load_levels)] for _ in range(num_graphics_load_levels)] for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]

    print("Starting benchmark...")

    for ml_index in range(num_mem_levels):
        ml = int(mem_levels[ml_index])
        for gl in graphics_levels[ml_index]:
            gl_index = graphics_levels[0].index(gl)
            gl = int(gl)
            print("benchmarking: " + str(gl) + "MHz/" + str(ml) + "MHz")
            graphics_load_level_index = 0
            for mat_size in range(mat_min, mat_max, mat_step):
                mem_load_level_index = 0
                for tmat_size in tmat_range:
                    print(graphics_load_level_index, mem_load_level_index)
                    d_mat = cp.empty(shape=(mat_size,mat_size))
                    d_tmat = cp.cuda.alloc(tmat_size * tmat_size * elem_size)
                    mt = DenseMatMulThread(d_mat, mat_size)
                    cpt = DenseTransposeThread(d_tmat, tmat_size)
                    tt.sleep(reset_period) #cooldown after matrix creation
                    pynvml.nvmlDeviceSetGpuLockedClocks(handle, gl, gl)
                    pynvml.nvmlDeviceSetMemoryLockedClocks(handle, ml, ml)
                    graphics_util, mem_util, energy, time = measure_benchmark(mt, cpt)
                    energies[gl_index][ml_index][graphics_load_level_index][mem_load_level_index] = energy
                    utilisations_graphics[gl_index][ml_index][graphics_load_level_index][mem_load_level_index] = graphics_util
                    utilisations_mem[gl_index][ml_index][graphics_load_level_index][mem_load_level_index] = mem_util 
                    execution_times[gl_index][ml_index][graphics_load_level_index][mem_load_level_index] = time                                                                                      
                    mem_load_level_index += 1
                    tt.sleep(reset_period) #rest to allow processor to reset
                graphics_load_level_index += 1
            suffix = str(device_index) + '_' + str(gl) + '_' + str(ml) + time_created()
            utils_combined = combine(np.array(utilisations_graphics[gl_index][ml_index]), np.array(utilisations_mem[gl_index][ml_index]))
            create_latex_2D(results_path + "/energies_" + suffix, energies[gl_index][ml_index], gl, ml)
            create_latex_2D(results_path + "/utils_" + suffix, utils_combined, gl, ml)
            create_csv(results_path + "/energies_" + suffix, energies[gl_index][ml_index])
            create_csv(results_path + "/utils_graphics_" + suffix, utilisations_graphics[gl_index][ml_index])
            create_csv(results_path + "/utils_mem_" + suffix, utilisations_mem[gl_index][ml_index])
            create_csv(results_path + "/execution_times_" + suffix, execution_times[gl_index][ml_index])
    return energies, utilisations_graphics, utilisations_mem, execution_times

def main(level_vals, device_index_val):

    #initialise level arrays
    global graphics_levels
    global mem_levels
    global num_graphics_levels
    global num_mem_levels
    mem_levels = level_vals[0]
    graphics_levels = level_vals[1:]
    num_graphics_levels = len(graphics_levels[0])
    num_mem_levels = len(mem_levels)

    #initialise path for results
    global results_path
    results_path = "results/" + str(date.today())
    os.mkdir(results_path)

    #initialise nvml and run benchmarks
    global device_index
    global handle
    global pm
    device_index = device_index_val
    pm = zeus_power.PowerMonitor(gpu_indices=list([device_index]), update_period=update_period)
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
    pynvml.nvmlDeviceSetPersistenceMode(handle, 1)

    measured_energies, measured_utils_graphics, measured_utils_mem, execution_times = run_benchmark()

    #shut down NVML
    pynvml.nvmlDeviceSetPersistenceMode(handle, 0)
    pynvml.nvmlShutdown()

    #write to output files
    device_str = str(device_index)
    suffix = device_str + time_created()
    measured_utils_combined = combine(np.array(measured_utils_graphics), np.array(measured_utils_mem))
    create_latex("results/energies_" + suffix, measured_energies, str(device_index))
    create_latex("results/utils_" + suffix, measured_utils_combined, str(device_index))
    create_csv_4D("results/energies_" + suffix, measured_energies)
    create_csv_4D("results/utils_graphics_" + suffix, measured_utils_graphics)
    create_csv_4D("results/utils_mem_" + suffix, measured_utils_mem)
    create_csv_4D("results/execution_times" + suffix, execution_times)

    #update symlinks
    os.unlink("energies_" + device_str + "-latest")
    os.unlink("utils_graphics_" + device_str + "-latest")
    os.unlink("utils_memory_" + device_str + "-latest")
    os.symlink("energies_" + suffix, "energies_" + device_str + "-latest")
    os.symlink("utils_graphics_" + suffix, "utils_graphics_" + device_str + "-latest")
    os.symlink("utils_mem_" + suffix, "utils_memory_" + device_str + "-latest")

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int, help="index of device to be profiled")
    args = parser.parse_args()

    main(parse_profile(args.device), args.device)