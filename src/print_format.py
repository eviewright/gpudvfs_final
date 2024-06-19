import argparse
import csv
import time as tt
import numpy as np
from cfg import num_graphics_load_levels, num_mem_load_levels

precision=4

#returns pretty-printed string with current date and time, for use in file names
def time_created(): return '_' + tt.strftime("%Y-%m-%d_%H:%M", tt.gmtime())

#read in csv containing gpu profile
def parse_profile(device_index):
    profile = read_in_csv("profile_" + str(device_index))
    graphics = profile[:2]
    extra_freqs = set()
    for freqs in profile[2:]:
        isect = [f for f in freqs if f in profile[1]]
        if isect == []:
            extra_freqs.update(freqs)
        graphics.append(isect)
    for gs in graphics[1:]:
        gs.extend(extra_freqs)
        gs.sort(reverse=True)
    return graphics

#transform two arrays into a single array of two-tuples
def combine(ag, am): return np.rec.fromarrays([ag, am]).tolist()

#transform a single array of two-tuples into two separate arrays
def decouple4D(arr): 
    arr_ret1 = np.ones_like(arr)
    arr_ret2 = np.ones_like(arr)
    for gdx in range(len(arr)):
            for mdx in range(len(arr[gdx])):
                for gldx in range(len(arr[gdx][mdx])):
                    for mldx in range(len(arr[gdx][mdx][gldx])):
                        (v1, v2) = arr[gdx][mdx][gldx][mldx]
                        arr_ret1[gdx][mdx][gldx][mldx] = v1
                        arr_ret2[gdx][mdx][gldx][mldx] = v2
    return arr_ret1, arr_ret2

#parse a string representation of a utilisation or energy measurement
def parse(s):
      if s == "N/A": 
          return -1
      elif s == "(N/A, N/A)":
          return (-1, -1)
      elif ('(' not in s) & ('[' not in s):
          #non-tuple value
          return float(s)
      else:
        #tuple value
        split = s.split(", ")
        return (float(split[0][1:]), float(split[1][:-1]))

# csv (de)formatting
def create_csv(filename, arr):
    with open(filename + ".csv", 'x', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(arr)

def create_csv_4D(filename, arr):
    with open(filename + ".csv", 'x', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for dim in arr:
            for dim2 in dim:
                writer.writerows(dim2)
                writer.writerow([])
            writer.writerow([])

def read_in_csv(filename):
    with open(filename + ".csv", 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        arr = []
        for row in reader:
            arr_row = []
            #read row into array
            for val in row:
                arr_row.append(float(val) if val != "N/A" else -1)
            arr.append(arr_row)
    return arr

def read_in_csv_4D(filename, delim=' '):
    with open(filename + ".csv", 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delim)
        arr = []
        arr_row_1 = []
        arr_row_2 = []
        second_empty = False
        for row in reader:
            if (row == []) & ~second_empty:
                arr_row_1.append(arr_row_2)
                arr_row_2 = []
                second_empty = True
            elif (row == []) & second_empty:
                arr.append(arr_row_1)
                arr_row_1 = []
                second_empty = False
            else:
                #read row into array
                stripped_row = [val.strip("| ") for val in row]
                arr_row_2.append([parse(val) for val in stripped_row if val != ""])
                second_empty = False
    return arr

# LaTeX-style table (de)formatting
def read_in_latex(filename, device):
    levels = parse_profile(device)
    num_mem_levels = len(levels[0])
    num_graphics_levels = len(levels[1])
    arr = [[[[-1 for _ in range(num_mem_load_levels)] for _ in range(num_graphics_load_levels)] for _ in range(num_mem_levels)] for _ in range(num_graphics_levels)]
    file = open(filename, 'r')
    lns = file.readlines()
    file.close
    gdx = 0
    mdx = 0
    second_empty = False
    for ln in lns:
        if (ln.strip() == ""): #empty lines - in between tables
            if not second_empty:
                mdx += 1
                if mdx == num_mem_levels:
                    gdx += 1
                    mdx = 0
                second_empty = True
        elif ('\\' not in ln): #ignore LaTeX-specific lines
            vals = ln.split(" & ")
            gl = int(vals[0])
            for i in range(num_mem_load_levels):
              arr[gdx][mdx][gl][i] = parse(vals[i + 1]) 
            second_empty = False
        else:
            second_empty = False    
    return arr

def create_latex_2D(filename, arr, gl, ml):
    begin_table = "\\begin{table}[ht]" + '\n' + '\scalebox{0.5} {' + '\n' + "  \\begin{tabular}{|c| c c c c c c c c |}" + '\n' +  "   \hline" + '\n' + "    & 0 & 1 & 2 & 3 & 4 & 5 & 6 & 7 \\\\" + '\n' + "    \hline"
    end_table = "   \hline" + '\n' + "   \end{tabular}}" + '\n' + "   \caption{Core Frequency: " + str(gl) + "MHz, Memory Frequency: " + str(ml) + "MHz}" + '\n' + "\end{table}" + '\n\n'

    def string_of(val):
        return "N/A" if (val == -1) | (val == (-1, -1)) else str(round(val, precision))

    with open(filename + ".txt", 'x') as file:
                print(begin_table, file=file)
                for gldx in range(len(arr)):
                    string = str(gldx) + " & "
                    for mll in arr[gldx]:
                        if isinstance(mll, float):
                            string += string_of(mll) + " & "
                        else:
                            (mlla, mllb) = mll
                            string +=  '(' + string_of(mlla) + ', ' + string_of(mllb) + ')' + " & "
                    print(string, sep="", file=file)
                print(end_table, sep="", file=file)

def create_latex(filename, arr, device):
    levels = parse_profile(device)
    graphics_levels = levels[1]
    mem_levels = levels[0]

    begin_table = "\\begin{table}[ht]" + '\n' + '\scalebox{0.58} {' + '\n' + "  \\begin{tabular}{|c| c c c c c c c |}" + '\n' +  "   \hline" + '\n' + "    & 0 & 1 & 2 & 3 & 4 & 5 & 6 \\\\" + '\n' + "    \hline"
    def end_table(g, m): 
        return "   \hline" + '\n' + "   \end{tabular}}" + '\n' + "   \caption{Core Frequency: " + str(graphics_levels[g]) + "MHz, Memory Frequency: " + str(mem_levels[m]) + "MHz}" + '\n' + "\end{table}" + '\n\n'

    def string_of(val):
        return "N/A" if (val == -1) | (val == (-1, -1)) else str(round(val, precision))

    with open(filename + ".txt", 'x') as file:
        for gdx in range(len(arr)):
            for mdx in range(len(arr[gdx])):
                print(begin_table, file=file)
                for gldx in range(len(arr[gdx][mdx])):
                    string = str(gldx) + " & "
                    for mll in arr[gdx][mdx][gldx]:
                        if isinstance(mll, float):
                            string += string_of(mll) + " & "
                        else:
                            (mlla, mllb) = mll
                            string +=  '(' + string_of(mlla) + ', ' + string_of(mllb) + ')' + " & "
                    print(string, sep="", file=file)
                print(end_table(gdx, mdx), sep="", file=file)

def main(device, in_file, out_file):
    #easy file conversion
    in_suffix = in_file[-4:]
    arr = read_in_csv_4D(in_file[:-4]) if in_suffix == ".csv" else read_in_latex(in_file, device)
    if out_file == "decouple":
        #split input utilisations file into graphics/memory constituents
        arr_g, arr_m = decouple4D(arr)
        create_csv_4D(in_file[:-4] + "_graphics", arr_g)
        create_csv_4D(in_file[:-4] + "_mem", arr_m)
    else:
        out_suffix = out_file[-4:]
        create_csv_4D(out_file[:-4], arr) if out_suffix == ".csv" else create_latex(out_file[:-4], arr, device)

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("device", type=int)
    parser.add_argument("in_file")
    parser.add_argument("out_file")
    args = parser.parse_args()
    main(args.device, args.in_file, args.out_file)   