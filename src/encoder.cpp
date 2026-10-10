#include "pcbl.h"
#include <omp.h>

void PhaseLattice::route_text_prompt(const std::string& prompt) {
    std::vector<uint64_t> generated_signature;
    uint64_t current_chunk = 0;
    for (size_t i = 0; i < prompt.length(); ++i) {
        current_chunk = (current_chunk << 8) | static_cast<uint64_t>(prompt[i]);
        if (i % 8 == 7 || i == prompt.length() - 1) {
            current_chunk ^= (current_chunk >> 33);
            current_chunk *= 0xFF51AFD7ED558CCDULL;
            generated_signature.push_back(current_chunk);
            current_chunk = 0;
        }
    }
    while (generated_signature.size() < 4) {
        generated_signature.push_back(0x5A5A5A5A5A5A5A5AULL);
    }
    size_t sig_size = generated_signature.size();
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < chunk_count; ++i) {
        uint64_t incoming_phase = generated_signature[i % sig_size];
        uint64_t intermediate = lattice_map[i] ^ incoming_phase;
        uint64_t next_state = (intermediate << 1) | (intermediate >> 63) | ~lattice_map[i];
        lattice_map[i] = (structural_locks[i] & lattice_map[i]) | (~structural_locks[i] & next_state);
    }
}

void PhaseLattice::mutate_and_lock_phase(const std::vector<uint64_t>& target_objective_signature) {
    size_t sig_size = target_objective_signature.size();
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < chunk_count; ++i) {
        uint64_t target = target_objective_signature[i % sig_size];
        uint64_t resonance = ~(lattice_map[i] ^ target);
        uint64_t mutation_perturbation = lattice_map[i] ^ 0x0F0F0F0F0F0F0F0FULL;
        structural_locks[i] |= (resonance & 0xCCCC0000CCCC0000ULL);
        lattice_map[i] = (structural_locks[i] & lattice_map[i]) | (~structural_locks[i] & mutation_perturbation);
    }
}

std::string PhaseLattice::generate_response_string(const std::string& input_prompt, size_t max_chars) {
    this->route_text_prompt(input_prompt);
    std::string response = "";
    const char token_map[] = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_!.-";
    size_t map_size = sizeof(token_map) - 1;
    for (size_t i = 0; i < max_chars; ++i) {
        size_t matrix_idx = (i * 13) % chunk_count;
        uint64_t raw_signal = lattice_map[matrix_idx] ^ structural_locks[matrix_idx];
        size_t token_index = (raw_signal ^ (i * 0x9E3779B9ULL)) % map_size;
        response += token_map[token_index];
    }
    return response;
}
