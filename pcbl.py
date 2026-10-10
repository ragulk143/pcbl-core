import ctypes
import os
import sys

class LocalBrainEngine:
    def __init__(self, num_elements: int, use_gpu: bool = False):
        # 1. Register your MinGW compiler folder so Python can locate libgomp / OpenMP dependencies
        compiler_bin = "C:/zohra-arts/mingw64/bin"
        if os.path.exists(compiler_bin):
            os.add_dll_directory(compiler_bin)

        # 2. Map the production build output path
        library_path = os.path.abspath("C:/zohra-arts/pcblV1/build/libpcbl_shared.dll")
        
        if not os.path.exists(library_path):
            raise FileNotFoundError(f"Could not locate libpcbl_shared.dll at: {library_path}")

        # 3. Load the library with full Win32 dependency search permissions (winmode=0)
        if sys.platform == 'win32':
            self.lib = ctypes.CDLL(library_path, winmode=0)
        else:
            self.lib = ctypes.CDLL(library_path)
            
        self.device_mode = 1 if use_gpu else 0
        
        self.lib.create_lattice.argtypes = [ctypes.c_size_t, ctypes.c_int]
        self.lib.create_lattice.restype = ctypes.c_void_p
        self.lib.route_text.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.get_convergence.argtypes = [ctypes.c_void_p]
        self.lib.get_convergence.restype = ctypes.c_double
        self.lib.get_response.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
        
        self.obj = self.lib.create_lattice(num_elements, self.device_mode)

    def learn_string(self, text: str):
        self.lib.route_text(self.obj, text.encode('utf-8'))

    def get_lock_saturation(self) -> float:
        return self.lib.get_convergence(self.obj)

    def query(self, prompt: str, max_output_chars: int = 50) -> str:
        buffer = ctypes.create_string_buffer(max_output_chars + 1)
        self.lib.get_response(self.obj, prompt.encode('utf-8'), buffer, max_output_chars)
        return buffer.value.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    print("[Python Suite] Booting 2-Billion parameter matrix on HOST CPU CACHE...")
    cpu_brain = LocalBrainEngine(num_elements=2000000000, use_gpu=False)
    
    prompt = "decentralized_universal_hardware_matrix_pass"
    print(f"[Python CPU State] Streaming training prompt sequence: '{prompt}'")
    cpu_brain.learn_string(prompt)
    
    print(f"[Python CPU State] Saturated Convergence: {cpu_brain.get_lock_saturation()}%")
    print(f"[Python CPU State] Response Synthesis: '{cpu_brain.query(prompt)}'")
