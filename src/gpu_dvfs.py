import argparse
import time as tt
import pynvml
from print_format import read_in_csv_4D, parse_profile

#constants
gpu_clock = 0
memory_clock = 2
execution_frequency = 0.1

def set_graphics_freq_level(freq):
    pynvml.nvmlDeviceSetGpuLockedClocks(handle, int(freq), int(freq))

def set_mem_freq_level(freq):
    pynvml.nvmlDeviceSetMemoryLockedClocks(handle, int(freq), int(freq))

def alter_frequency():
    
    #get current graphics\memory level from current frequency
    def get_curr_level(f, arr):
        for i in range(len(arr)):
            if f <= arr[i]:
                return i
        return len(arr) - 1
    
    global curr_temp
    global previous_temperature
    
    #check whether to penalise for temperature rise
    def delta_for_temperature(new_g):
        return -1 if curr_temp > previous_temperature and new_g >= curr_graphics_freq_level else 0
            
    #get current state
    graphics_clock_speed = pynvml.nvmlDeviceGetClockInfo(handle, gpu_clock)
    curr_graphics_freq_level = get_curr_level(graphics_clock_speed, graphics_levels)
    mem_clock_speed = pynvml.nvmlDeviceGetClockInfo(handle, memory_clock)
    curr_mem_freq_level = get_curr_level(mem_clock_speed, mem_levels)
    if account_temperature:
        curr_temp = pynvml.nvmlDeviceGetTemperature(handle, 0)

    #get optimal utilisation ranges for current frequencies
    u_low_graphics = u_lows_graphics[curr_graphics_freq_level][curr_mem_freq_level]
    u_low_mem = u_lows_mem[curr_graphics_freq_level][curr_mem_freq_level]
    u_up_graphics = u_ups_graphics[curr_graphics_freq_level][curr_mem_freq_level]
    u_up_mem = u_ups_mem[curr_graphics_freq_level][curr_mem_freq_level]

    #get current utilisations
    utils = pynvml.nvmlDeviceGetUtilizationRates(handle)

    #calculate next frequencies
    if utils.gpu == 0:
        new_graphics_level = 0
        has_increased = False
    elif utils.gpu <= u_low_graphics:
        scale_frequency_factor = (int) (u_low_graphics // utils.gpu)
        new_graphics_level = curr_graphics_freq_level - scale_frequency_factor
        has_increased = False
    elif utils.gpu >= u_up_graphics:
        new_graphics_level = curr_graphics_freq_level + 2 if increase_count else curr_graphics_freq_level + 1
        has_increased = True
    else:
        new_graphics_level = curr_graphics_freq_level
        has_increased = False
    if utils.memory == 0:
        new_mem_level = 0
    elif utils.memory <= u_low_mem:
        scale_frequency_factor = (int) (u_low_mem // utils.memory)
        new_mem_level = curr_mem_freq_level - scale_frequency_factor
    elif utils.memory >= u_up_mem:
        new_mem_level = curr_mem_freq_level + 1 
    else:
        new_mem_level = curr_mem_freq_level

    #penalise for high temperature if using temperature-aware governor
    if account_temperature:
        delta_g, delta_m = delta_for_temperature(new_graphics_level, new_mem_level)
        new_graphics_level += delta_g
        new_mem_level += delta_m
        previous_temperature = curr_temp

    #ensure that new level is valid
    new_graphics_level = max(new_graphics_level, 0)
    new_mem_level = max(new_mem_level, 0)
    new_graphics_level = min(new_graphics_level, num_graphics_levels - 1)
    new_mem_level = min(new_mem_level, num_mem_levels - 1)

    #set new levels
    set_graphics_freq_level(graphics_levels[new_graphics_level])
    set_mem_freq_level(mem_levels[new_mem_level])

    return has_increased
    

def main(level_vals, u_lows_graphics_vals, u_lows_mem_vals, u_ups_graphics_vals, u_ups_mem_vals, device_index, usetemperature):
    
    #globals
    global u_lows_graphics
    global u_ups_graphics
    global u_lows_mem
    global u_ups_mem
    global graphics_levels
    global num_graphics_levels
    global mem_levels
    global num_mem_levels
    global increase_count
    global handle
    global account_temperature
    global curr_temp
    global previous_temperature

    #initialise globals
    u_lows_graphics = u_lows_graphics_vals
    u_ups_graphics = u_ups_graphics_vals
    u_lows_mem = u_lows_mem_vals
    u_ups_mem = u_ups_mem_vals
    mem_levels = level_vals[0][::-1]
    num_mem_levels = len(mem_levels)
    graphics_levels = level_vals[1][::-1]
    num_graphics_levels = len(graphics_levels)
    increase_count = False
    account_temperature = usetemperature

    #initialise nvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
    pynvml.nvmlDeviceSetPersistenceMode(handle, 1)
    
    #take initial temperature measurement
    curr_temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
    previous_temperature = curr_temp

    #perform dvfs
    while True:
        increase_count = alter_frequency()
        tt.sleep(execution_frequency)
    
if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int, help="index of device to be profiled")
    parser.add_argument('-temp', '--usetemperature', action='store_true')
    parser.add_argument('-avg', '--average', action='store_true')
    args = parser.parse_args()

    #read in optimal utilisation boundaries
    utils_low_g = read_in_csv_4D("utils_low_g_average_" + str(args.device)) if args.average else read_in_csv_4D("utils_low_g_" + str(args.device))
    utils_low_m = read_in_csv_4D("utils_low_m_average_" + str(args.device)) if args.average else read_in_csv_4D("utils_low_m_" + str(args.device))
    utils_up_g = read_in_csv_4D("utils_up_g_average_" + str(args.device)) if args.average else read_in_csv_4D("utils_up_g_" + str(args.device))
    utils_up_m = read_in_csv_4D("utils_up_m_average_" + str(args.device)) if args.average else read_in_csv_4D("utils_up_m_" + str(args.device))

    main(parse_profile(args.device), utils_low_g, utils_low_m, utils_up_g, utils_up_m, args.device, args.usetemperature)