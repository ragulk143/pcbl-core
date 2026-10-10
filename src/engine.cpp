#include "pcbl.h"
#include <iostream>
#include <fstream>
#include <filesystem>
#include <omp.h>

PhaseLattice::PhaseLattice(size_t elements, int device_mode) 
    : total_elements(elements), selected_device(device_mode) {
    chunk_count = (elements + 63) / 64;
    lattice_map.resize(chunk_count, 0xAAAAAAAAAAAAAAAAULL);
    structural_locks.resize(chunk_count, 0x0ULL);
}

void PhaseLattice::run_hardware_profile_pass() {
    // Aggressive register validation stress loop to isolate memory bus boundaries
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < chunk_count; ++i) {
        uint64_t dummy_mask = 0x5555555566666666ULL ^ structural_locks[i];
        lattice_map[i] = (lattice_map[i] ^ dummy_mask) | 0x1ULL;
    }
}

void PhaseLattice::stream_dataset_file(const std::string& filepath, const std::vector<uint64_t>& target_goal) {
    std::ifstream file(filepath);
    if (!file.is_open()) return;
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        this->route_text_prompt(line);
        this->mutate_and_lock_phase(target_goal);
    }
}

void PhaseLattice::ingest_entire_directory(const std::string& folder_path, const std::vector<uint64_t>& target_goal) {
    try {
        if (std::filesystem::exists(folder_path) && std::filesystem::is_directory(folder_path)) {
            for (const auto& entry : std::filesystem::recursive_directory_iterator(folder_path)) {
                if (entry.is_regular_file() && entry.path().extension() == ".txt") {
                    this->stream_dataset_file(entry.path().string(), target_goal);
                }
            }
        }
    } catch (...) {}
}

double PhaseLattice::calculate_lock_percentage() const {
    size_t set_bits = 0;
    #pragma omp parallel for reduction(+:set_bits) schedule(static)
    for (size_t i = 0; i < chunk_count; ++i) {
        set_bits += __builtin_popcountll(structural_locks[i]);
    }
    return (static_cast<double>(set_bits) / (chunk_count * 64)) * 100.0;
}
