import argparse
import pynvml
from print_format import create_csv

def main(device_index, gprop, mprop):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
    #query memory frequencies supported by GPU
    mem_clocks = pynvml.nvmlDeviceGetSupportedMemoryClocks(handle=handle)
    
    sublists = [[] for _ in range(len(mem_clocks) // mprop + 1)]
    for mcdx in range(0, len(mem_clocks), mprop):
        memHz = mem_clocks[mcdx]
        sublists[0].append(memHz)
        #query graphics frequencies supported by GPU alongside memory frequency
        graphics_clocks = pynvml.nvmlDeviceGetSupportedGraphicsClocks(handle, memHz)
        #add every g_prop'th graphics clock supported for that frequency   
        for gcdx in range(0, len(graphics_clocks), gprop):
            sublists[mcdx + 1].append(graphics_clocks[gcdx])
    
    create_csv("profile_" + str(device_index), sublists)

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int, help="index of device to be profiled")
    parser.add_argument("gprop", type=int, help="define the proportion of available graphics frequency settings used for benchmarking and scaling")
    parser.add_argument("mprop", type=int, help="define the proportion of available memory frequency settings used for benchmarking and scaling")
    args = parser.parse_args()
    main(args.device, args.gprop, args.mprop)






