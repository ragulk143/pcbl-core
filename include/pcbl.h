#ifndef PCBL_H
#define PCBL_H

#include <vector>
#include <cstdint>
#include <string>
#include <cstddef>
#include <algorithm>

class PhaseLattice {
private:
    size_t total_elements;
    size_t chunk_count;
    std::vector<uint64_t> lattice_map;
    std::vector<uint64_t> structural_locks;
    int selected_device;

public:
    PhaseLattice(size_t elements, int device_mode);
    
    void route_text_prompt(const std::string& prompt);
    void route_image_pixel_stream(const std::vector<uint8_t>& pixel_bytes);
    void run_hardware_profile_pass();
    
    // Core Topology Visualizer: Extract a memory grid slice for bitwise text art rendering
    void extract_topology_slice(size_t chunk_offset, uint64_t* out_lattice, uint64_t* out_locks, size_t count) const;
    
    void mutate_and_lock_phase(const std::vector<uint64_t>& target_objective_signature);
    void stream_dataset_file(const std::string& filepath, const std::vector<uint64_t>& target_goal);
    void ingest_entire_directory(const std::string& folder_path, const std::vector<uint64_t>& target_goal);
    
    double calculate_lock_percentage() const;
    bool export_to_binary_checkpoint(const std::string& filepath) const;
    bool import_from_binary_checkpoint(const std::string& filepath);
    std::string generate_response_string(const std::string& input_prompt, size_t max_chars);

    size_t get_chunk_count() const { return chunk_count; }
};

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) inline PhaseLattice* create_lattice(size_t elements, int device_mode) {
    return new PhaseLattice(elements, device_mode);
}

__declspec(dllexport) inline void free_lattice(PhaseLattice* ptr) {
    delete ptr;
}

__declspec(dllexport) inline void route_text(PhaseLattice* ptr, const char* text) {
    ptr->route_text_prompt(std::string(text));
}

__declspec(dllexport) inline void route_pixels(PhaseLattice* ptr, const uint8_t* bytes, size_t length) {
    std::vector<uint8_t> pixel_vec(bytes, bytes + length);
    ptr->route_image_pixel_stream(pixel_vec);
}

__declspec(dllexport) inline void profile_hardware(PhaseLattice* ptr) {
    ptr->run_hardware_profile_pass();
}

__declspec(dllexport) inline double get_convergence(PhaseLattice* ptr) {
    return ptr->calculate_lock_percentage();
}

// C-Bridge Export Hook: Allow Python to capture memory snapshot arrays
__declspec(dllexport) inline void get_topology_slice(PhaseLattice* ptr, size_t offset, uint64_t* out_lat, uint64_t* out_lck, size_t count) {
    ptr->extract_topology_slice(offset, out_lat, out_lck, count);
}

__declspec(dllexport) inline void get_response(PhaseLattice* ptr, const char* prompt, char* out_buf, size_t max_chars) {
    std::string res = ptr->generate_response_string(std::string(prompt), max_chars);
    size_t copy_len = (std::min)(res.size(), max_chars);
    std::copy_n(res.begin(), copy_len, out_buf);
    out_buf[copy_len] = '\0';
}

__declspec(dllexport) inline bool export_to_binary_checkpoint(PhaseLattice* ptr, const char* filepath) {
    return ptr->export_to_binary_checkpoint(std::string(filepath));
}

__declspec(dllexport) inline bool import_from_binary_checkpoint(PhaseLattice* ptr, const char* filepath) {
    return ptr->import_from_binary_checkpoint(std::string(filepath));
}

#ifdef __cplusplus
}
#endif

#endif
