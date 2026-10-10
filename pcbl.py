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
        
        self.lib.create_lattice.argtypes = [ctypes.c_size_t, ctypes.c_int]
        self.lib.create_lattice.restype = ctypes.c_void_p
        self.lib.route_text.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        # New Linkage Hook: Bind Python types to the raw pixel array endpoints
        self.lib.route_pixels.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        
        self.lib.get_convergence.argtypes = [ctypes.c_void_p]
        self.lib.get_convergence.restype = ctypes.c_double
        self.lib.get_response.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
        
        self.obj = self.lib.create_lattice(num_elements, self.device_mode)

    def learn_string(self, text: str):
        self.lib.route_text(self.obj, text.encode('utf-8'))

    def learn_image_pixels(self, pixel_list: list):
        # Compress the python integer list directly into native C-style uint8 arrays
        array_type = ctypes.c_uint8 * len(pixel_list)
        c_array = array_type(*pixel_list)
        self.lib.route_pixels(self.obj, c_array, len(pixel_list))

    def get_lock_saturation(self) -> float:
        return self.lib.get_convergence(self.obj)

    def query_raw(self, prompt: str, max_output_chars: int = 1) -> str:
        buffer = ctypes.create_string_buffer(max_output_chars + 1)
        self.lib.get_response(self.obj, prompt.encode('utf-8'), buffer, max_output_chars)
        return buffer.value.decode('utf-8', errors='ignore')

    def generate_streaming(self, initial_prompt: str, tokens_to_generate: int = 40):
        print(f"\n[Multi-Modal Output] Context prompt: \"{initial_prompt}\"")
        print("[Multi-Modal Output] Generated Text: ", end="", flush=True)
        current_context = initial_prompt
        for _ in range(tokens_to_generate):
            next_token = self.query_raw(current_context, max_output_chars=1)
            if not next_token:
                next_token = " "
            print(next_token, end="", flush=True)
            current_context += next_token
            time.sleep(0.01)
        print("\n")

if __name__ == "__main__":
    print("[Multi-Modal Brain] Initializing 2-Billion parameter unified bit-lattice...")
    brain = LocalBrainEngine(num_elements=2000000000, use_gpu=False)
    
    # 1. Stream text data
    print("[Multi-Modal Brain] Processing textual token lines...")
    brain.learn_string("ingesting cross modal datasets natively")
    
    # 2. Stream visual pixel data! Simulate a 1024-byte RGB image matrix array
    mock_pixel_data = [(i % 256) for i in range(1024)]
    print(f"[Multi-Modal Brain] Processing visual array stream ({len(mock_pixel_data)} pixel bytes)...")
    
    auto_start = time.perf_counter()
    brain.learn_image_pixels(mock_pixel_data)
    auto_end = time.perf_counter()
    
    print(f"[Multi-Modal Brain] Visual pixel frame ingested in: {(auto_end - auto_start)*1000:.2f} ms")
    print(f"[Multi-Modal Brain] Parameter convergence: {brain.get_lock_saturation()}%")
    
    # 3. Query text output based on the combined cross-modal tracking states
    brain.generate_streaming(initial_prompt="image_perception_vector", tokens_to_generate=50)
