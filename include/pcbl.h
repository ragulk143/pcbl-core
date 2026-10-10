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

// Fixed: Explicitly export functions so Windows lets Python find them
__declspec(dllexport) inline PhaseLattice* create_lattice(size_t elements, int device_mode) {
    return new PhaseLattice(elements, device_mode);
}

__declspec(dllexport) inline void free_lattice(PhaseLattice* ptr) {
    delete ptr;
}

__declspec(dllexport) inline void route_text(PhaseLattice* ptr, const char* text) {
    ptr->route_text_prompt(std::string(text));
}

__declspec(dllexport) inline double get_convergence(PhaseLattice* ptr) {
    return ptr->calculate_lock_percentage();
}

__declspec(dllexport) inline void get_response(PhaseLattice* ptr, const char* prompt, char* out_buf, size_t max_chars) {
    std::string res = ptr->generate_response_string(std::string(prompt), max_chars);
    size_t copy_len = (std::min)(res.size(), max_chars);
    std::copy_n(res.begin(), copy_len, out_buf);
    out_buf[copy_len] = '\0';
}

#ifdef __cplusplus
}
#endif

#endif
