#ifndef LATTICE_H
#define LATTICE_H

#include <vector>
#include <cstdint>
#include <cstddef>
#include <string>

class PhaseLattice {
private:
    size_t total_elements;
    size_t chunk_count;
    std::vector<uint64_t> lattice_map;
    std::vector<uint64_t> structural_locks;

public:
    PhaseLattice(size_t elements);
    
    void route_text_prompt(const std::string& prompt);
    void mutate_and_lock_phase(const std::vector<uint64_t>& target_objective_signature);
    void stream_dataset_file(const std::string& filepath, const std::vector<uint64_t>& target_goal);
    
    // Core Upgrades: High-throughput directory execution and lock convergence metrics
    void ingest_entire_directory(const std::string& folder_path, const std::vector<uint64_t>& target_goal);
    double calculate_lock_percentage() const;

    std::string generate_response_string(const std::string& input_prompt, size_t max_chars);

    uint64_t get_chunk(size_t index) const { return lattice_map[index]; }
    size_t get_chunk_count() const { return chunk_count; }
};

#endif
