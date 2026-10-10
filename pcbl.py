import ctypes
import os
import sys
import time

class LocalBrainEngine:
    def __init__(self, num_elements: int, use_gpu: bool = False):
        compiler_bin = "C:/zohra-arts/mingw64/bin"
        if os.path.exists(compiler_bin):
            os.add_dll_directory(compiler_bin)

        library_path = os.path.abspath("C:/zohra-arts/pcblV1/build/libpcbl_shared.dll")
        if not os.path.exists(library_path):
            raise FileNotFoundError(f"Could not locate libpcbl_shared.dll at: {library_path}")

        if sys.platform == 'win32':
            self.lib = ctypes.CDLL(library_path, winmode=0)
        else:
            self.lib = ctypes.CDLL(library_path)
            
        self.device_mode = 1 if use_gpu else 0
        self.num_elements = num_elements
        self.bytes_allocated = (num_elements // 8) * 2
        
        # Hardened pointer type mappings for massive 64-bit address bounds
        self.lib.create_lattice.argtypes = [ctypes.c_size_t, ctypes.c_int]
        self.lib.create_lattice.restype = ctypes.c_void_p
        
        self.lib.free_lattice.argtypes = [ctypes.c_void_p]
        self.lib.free_lattice.restype = None
        
        self.lib.profile_hardware.argtypes = [ctypes.c_void_p]
        self.lib.profile_hardware.restype = None
        
        self.obj = self.lib.create_lattice(num_elements, self.device_mode)

    def execute_hardware_profile(self) -> float:
        t_start = time.perf_counter()
        self.lib.profile_hardware(self.obj)
        t_end = time.perf_counter()
        return (t_end - t_start) * 1000.0

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj') and self.obj:
            # Safely pass the 64-bit memory block handle back to C++ for clean disposal
            self.lib.free_lattice(self.obj)
            self.obj = None

if __name__ == "__main__":
    print("==========================================================================")
    print("      SYSTEMS CONFIGURATION TELEMETRY INTERFACE: HARDWARE TEST SUITE      ")
    print("==========================================================================")
    
    target_scales = {
        "2-Billion Parameters": 2000000000,
        "4-Billion Parameters": 4000000000,
        "7-Billion Parameters": 7000000000
    }
    
    for label, size in target_scales.items():
        print(f"\n[Allocation Target] Provisioning {label} in memory space...")
        try:
            node = LocalBrainEngine(num_elements=size, use_gpu=False)
            mb_allocated = node.bytes_allocated / (1024 * 1024)
            print(f" -> Memory footprint on RAM bus: {mb_allocated:.2f} MB")
            
            for _ in range(3):
                node.execute_hardware_profile()
                
            pass_ms = node.execute_hardware_profile()
            
            gb_processed = node.bytes_allocated / 1e9
            seconds = pass_ms / 1000.0
            throughput_gbps = gb_processed / seconds if seconds > 0 else 0
            
            print(f" -> Execution pass duration   : {pass_ms:.3f} ms")
            print(f" -> Memory Bus Throughput Speed: {throughput_gbps:.2f} GB/s")
            
            # Trigger explicit deletion inside the loop to see clean allocation turnovers
            del node
            
        except Exception as e:
            print(f" -> [Allocation Warning] Matrix scale skipped: {e}")
            
    print("\n==========================================================================")
