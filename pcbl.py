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
        
        self.lib.create_lattice.argtypes = [ctypes.c_size_t, ctypes.c_int]
        self.lib.create_lattice.restype = ctypes.c_void_p
        self.lib.free_lattice.argtypes = [ctypes.c_void_p]
        self.lib.free_lattice.restype = None
        self.lib.route_text.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
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

    # UNLOCKED: The Space-Filtering Continuous Character Streamer
    def generate_continuous(self, initial_prompt: str, chars_to_generate: int = 40):
        print(f" -> Prompt Context Window: \"{initial_prompt}\"")
        print(" -> Dense Token Stream   : ", end="", flush=True)
        
        current_context = initial_prompt
        collected_chars = 0
        loop_safety = 0
        
        # Keep sampling until we gather the exact number of active, non-space characters requested
        while collected_chars < chars_to_generate and loop_safety < chars_to_generate * 4:
            next_token = self.query_raw(current_context, max_output_chars=1)
            
            # If the engine hits an untrained default zone, filter it out and skip
            if not next_token or next_token == " ":
                # Mutate context slightly using a pseudorandom step to skip past the empty matrix cluster
                current_context += "_"
                loop_safety += 1
                continue
                
            # Print the verified dense active character instantly
            print(next_token, end="", flush=True)
            current_context += next_token
            collected_chars += 1
            loop_safety += 1
            time.sleep(0.005)
        print("\n")

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj') and self.obj:
            self.lib.free_lattice(self.obj)
            self.obj = None

if __name__ == "__main__":
    print("==========================================================================")
    print("        PCBL PRODUCTION TESTING: FULL CONTINUOUS COMPOTENCY SYSTEM        ")
    print("==========================================================================")
    
    size_7b = 7000000000
    print(f"[Core Init] Initializing 7-Billion Unified Bit-Lattice Matrix...")
    brain = LocalBrainEngine(num_elements=size_7b, use_gpu=False)
    
    # -------------------------------------------------------------
    # TEST VECTOR 1: PURE TEXT INGESTION & DENSE TOKEN GENERATION
    # -------------------------------------------------------------
    print("\n[Test Run 1: Text Modality] Streaming English text context sequence...")
    brain.learn_string("hardware optimized token tracking layers bypass corporate servers natively")
    brain.generate_continuous(initial_prompt="pure_text_pipeline_evaluation", chars_to_generate=40)
    
    # -------------------------------------------------------------
    # TEST VECTOR 2: PURE IMAGE INGESTION & DENSE TOKEN GENERATION
    # -------------------------------------------------------------
    print("[Test Run 2: Vision Modality] Streaming 12KB raw structural visual bytes...")
    mock_pixels = [(i % 256) for i in range(12288)] # Generate 12KB image buffer layout
    brain.learn_image_pixels(mock_pixels)
    brain.generate_continuous(initial_prompt="pure_image_matrix_evaluation", chars_to_generate=40)
    
    # -------------------------------------------------------------
    # TEST VECTOR 3: COMBINED MULTI-MODAL INGESTION & GENERATION
    # -------------------------------------------------------------
    print("[Test Run 3: Multi-Modal Mixture] Fusing cross-modal text and pixel matrices...")
    brain.learn_string("विकेंद्रीकृत स्थानीय सिर्जनात्मकता") # Ingest Global Text
    brain.learn_image_pixels(mock_pixels) # Ingest Image Pixels again
    brain.generate_continuous(initial_prompt="multimodal_fused_lattice_evaluation", chars_to_generate=40)
    
    print("==========================================================================")
