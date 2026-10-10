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
        self.bytes_allocated = (num_elements // 8) * 2
        
        self.lib.create_lattice.argtypes = [ctypes.c_size_t, ctypes.c_int]
        self.lib.create_lattice.restype = ctypes.c_void_p
        self.lib.free_lattice.argtypes = [ctypes.c_void_p]
        self.lib.route_text.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        # Core Pixel Linkage: Explicitly map the 8-bit pointer array data boundaries
        self.lib.route_pixels.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        
        self.lib.get_convergence.argtypes = [ctypes.c_void_p]
        self.lib.get_convergence.restype = ctypes.c_double
        self.lib.get_response.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
        
        self.obj = self.lib.create_lattice(num_elements, self.device_mode)

    def learn_string(self, text: str):
        self.lib.route_text(self.obj, text.encode('utf-8'))

    def learn_image_pixels(self, pixel_list: list):
        array_type = ctypes.c_uint8 * len(pixel_list)
        c_array = array_type(*pixel_list)
        self.lib.route_pixels(self.obj, c_array, len(pixel_list))

    def get_lock_saturation(self) -> float:
        return self.lib.get_convergence(self.obj)

    def query_raw(self, prompt: str, max_output_chars: int = 1) -> str:
        buffer = ctypes.create_string_buffer(max_output_chars * 4 + 1)
        self.lib.get_response(self.obj, prompt.encode('utf-8'), buffer, max_output_chars)
        return buffer.value.decode('utf-8', errors='ignore')

    def generate_streaming(self, initial_prompt: str, tokens_to_generate: int = 40):
        print(f"\n[Cross-Modal Inference] Context input prompt: \"{initial_prompt}\"")
        print("[Cross-Modal Inference] Generated Response   : ", end="", flush=True)
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
    print("==========================================================================")
    print("        PCBL PRODUCTION RUNTIME TEST: MULTI-MODAL PIXEL VALIDATION       ")
    print("==========================================================================")
    
    size_7b = 7000000000
    print("[Initialization] Allocating 7-Billion parameter unified bit-lattice...")
    brain = LocalBrainEngine(num_elements=size_7b, use_gpu=False)
    
    # Pass 1: Ingest linguistic text domain knowledge data
    text_context = "multi modal perceptual alignment blends vision matrices with language strings"
    print(f"\n[Modality 1: Text] Ingesting token text sequence: \"{text_context}\"")
    brain.learn_string(text_context)
    
    # Pass 2: Ingest visual pixel data! Simulate a 64x64 pixel image frame with 3 channels (RGB)
    # Total array length = 64 * 64 * 3 = 12,288 raw bytes of structural geometric data
    print("\n[Modality 2: Vision] Generating mock 64x64 RGB structural pixel frame array...")
    mock_image_bytes = []
    for y in range(64):
        for x in range(64):
            # Inject a mathematical geometric wave gradient pattern directly into the RGB bytes
            r = (x * 4) % 256
            g = (y * 4) % 256
            b = (x + y) % 256
            mock_image_bytes.extend([r, g, b])
            
    print(f"[Modality 2: Vision] Streaming {len(mock_image_bytes)} pixel bytes through the memory bus...")
    
    v_start = time.perf_counter()
    brain.learn_image_pixels(mock_image_bytes)
    v_end = time.perf_counter()
    
    print(f"[Modality 2: Vision] Ingestion complete! 12KB pixel frame absorbed in: {(v_end - v_start)*1000:.2f} ms")
    print(f"[Telemetry Dashboard] Total matrix convergence state: {brain.get_lock_saturation()}%")
    
    # Pass 3: Trigger Cross-Modal Text Synthesis based on the combined text + pixel fields!
    brain.generate_streaming(initial_prompt="visual_image_sensor_perception", tokens_to_generate=50)
    print("==========================================================================")
