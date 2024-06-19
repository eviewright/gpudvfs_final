#configured globals used in multiple files
mat_min = 0
mat_max = 140
mat_step = 20
tmat_scale = 5
tmat_min = 0
tmat_max = (mat_max * tmat_scale)
num_graphics_load_levels = (mat_max - mat_min) // mat_step
tmat_range = list(range(tmat_min, tmat_max, mat_step * tmat_scale))
num_mem_load_levels = len(tmat_range)