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
        self.lib.get_convergence.argtypes = [ctypes.c_void_p]
        self.lib.get_convergence.restype = ctypes.c_double
        self.lib.get_response.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
        
        # Hardened Binary Serialization C-Bridge Hook Specifications
        self.lib.export_to_binary_checkpoint.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.export_to_binary_checkpoint.restype = ctypes.c_bool
        self.lib.import_from_binary_checkpoint.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.import_from_binary_checkpoint.restype = ctypes.c_bool
        
        self.obj = self.lib.create_lattice(num_elements, self.device_mode)

    def learn_string(self, text: str):
        self.lib.route_text(self.obj, text.encode('utf-8'))

    def get_lock_saturation(self) -> float:
        return self.lib.get_convergence(self.obj)

    def save_checkpoint(self, filepath: str) -> bool:
        return self.lib.export_to_binary_checkpoint(self.obj, filepath.encode('utf-8'))

    def load_checkpoint(self, filepath: str) -> bool:
        return self.lib.import_from_binary_checkpoint(self.obj, filepath.encode('utf-8'))

    def query_raw(self, prompt: str, max_output_chars: int = 1) -> str:
        buffer = ctypes.create_string_buffer(max_output_chars + 1)
        self.lib.get_response(self.obj, prompt.encode('utf-8'), buffer, max_output_chars)
        return buffer.value.decode('utf-8', errors='ignore')

    def generate_streaming(self, initial_prompt: str, tokens_to_generate: int = 40):
        print(f"\n[Inference Pass] Prompt context window: \"{initial_prompt}\"")
        print("[Inference Pass] Model Response: ", end="", flush=True)
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
    print("[Python Suite] Initializing 2-Billion parameter PCBL core engine...")
    brain = LocalBrainEngine(num_elements=2000000000, use_gpu=False)
    
    # 1. Run training sequences to flip parameters
    print("[Training Mode] Streaming raw bootstrap data lines into parameter layers...")
    brain.learn_string("decentralized local architecture framework training on consumer devices")
    
    # 2. Export the current trained state matrix directly to the hard drive path
    checkpoint_file = "python_pcbl_brain.bin"
    print(f"[Checkpoint Engine] Freezing state and exporting to: '{checkpoint_file}'...")
    if brain.save_checkpoint(checkpoint_file):
        print("[Checkpoint Engine] Binary checkpoint successfully serialized to disk!")
        
    # 3. Fire streaming prediction tokens out of memory
    brain.generate_streaming(initial_prompt="edge_computing", tokens_to_generate=50)
