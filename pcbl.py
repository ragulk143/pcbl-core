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
        
        # Hardened pointer type mappings for stable 64-bit reference address boundaries
        self.lib.create_lattice.argtypes = [ctypes.c_size_t, ctypes.c_int]
        self.lib.create_lattice.restype = ctypes.c_void_p
        self.lib.free_lattice.argtypes = [ctypes.c_void_p]
        self.lib.free_lattice.restype = None
        self.lib.route_text.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.get_convergence.argtypes = [ctypes.c_void_p]
        self.lib.get_convergence.restype = ctypes.c_double
        self.lib.get_response.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
        
        self.obj = self.lib.create_lattice(num_elements, self.device_mode)

    def learn_string(self, text: str):
        self.lib.route_text(self.obj, text.encode('utf-8'))

    def get_lock_saturation(self) -> float:
        return self.lib.get_convergence(self.obj)

    def query_raw(self, prompt: str, max_output_chars: int = 1) -> str:
        buffer = ctypes.create_string_buffer(max_output_chars + 1)
        self.lib.get_response(self.obj, prompt.encode('utf-8'), buffer, max_output_chars)
        return buffer.value.decode('utf-8', errors='ignore')

    # Autoregressive Streaming Next-Token Generation Loop
    def generate_streaming(self, initial_prompt: str, tokens_to_generate: int = 50):
        print(f"\n[Generative Pass] Prompt Context Window: \"{initial_prompt}\"")
        print("[Generative Pass] Synthesized Response : ", end="", flush=True)
        current_context = initial_prompt
        for _ in range(tokens_to_generate):
            next_token = self.query_raw(current_context, max_output_chars=1)
            if not next_token:
                next_token = " "
            print(next_token, end="", flush=True)
            current_context += next_token
            time.sleep(0.01)
        print("\n")

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj') and self.obj:
            self.lib.free_lattice(self.obj)
            self.obj = None

if __name__ == "__main__":
    print("==========================================================================")
    print("       PCBL USER INTERFACE: ACCELERATED 7-BILLION PARAMETER CORE          ")
    print("==========================================================================")
    
    # Instantiate the massive 7-Billion Parameter Local Matrix Grid
    size_7b = 7000000000
    print(f"[Initialization] Provisioning 7-Billion Connections in System RAM...")
    brain = LocalBrainEngine(num_elements=size_7b, use_gpu=False)
    
    mb_allocated = brain.bytes_allocated / (1024 * 1024)
    print(f"[Telemetry] Active memory footprint on RAM bus: {mb_allocated:.2f} MB")
    print(f"[Telemetry] Initial parameter lock convergence: {brain.get_lock_saturation()}%")
    
    # Stream real-world domain engineering data directly into the 7B memory bus
    knowledge_stream = "absolute architectural decentralization eliminates data center corporate dependencies natively"
    print(f"\n[Training Mode] Ingesting structured token sequence: \"{knowledge_stream}\"")
    
    t_start = time.perf_counter()
    brain.learn_string(knowledge_stream)
    t_end = time.perf_counter()
    
    print(f"[Training Mode] Ingestion complete in: {(t_end - t_start)*1000:.2f} ms")
    print(f"[Training Mode] Updated parameter lock convergence: {brain.get_lock_saturation()}%")
    
    # Trigger Autoregressive Token Generation out of the primed 7-Billion parameter topology lanes!
    brain.generate_streaming(initial_prompt="decentralized_intelligence_core", tokens_to_generate=50)
    print("==========================================================================")
