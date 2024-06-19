import threading
import cupy as cp
import cupy.cuda.runtime as crt

#constants
elem_size = 8
cudaMemcpyDeviceToDevice = 3
num_mul_reps = 500000
num_cpy_reps = 1250000

#thread performing dense matrix multiplications
class DenseMatMulThread(threading.Thread):

    def __init__(self, mat, mat_size):
        self.mat = mat
        self.mat_size = mat_size
        super(DenseMatMulThread, self).__init__()

    def run(self):
        if (self.mat_size != 0):      
            for _ in range(num_mul_reps):
                self.mat = cp.matmul(self.mat, self.mat)
        print("mfin")

#thread performing dense matrix memory copies
class DenseTransposeThread(threading.Thread):
    
    def __init__(self, d_tmat, tmat_size):
        self.d_tmat = d_tmat
        self.tmat_size = tmat_size
        self.alloc_size = tmat_size * tmat_size * elem_size
        super(DenseTransposeThread, self).__init__()

    def run(self):
        if (self.tmat_size != 0):
            for _ in range(num_cpy_reps): 
                dst = cp.cuda.alloc(self.alloc_size) 
                crt.memcpy(dst=dst.ptr, src=self.d_tmat.ptr, size=self.alloc_size, kind=3)
        print("tfin")