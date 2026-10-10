#include "pcbl.h"
#include <fstream>

bool PhaseLattice::export_to_binary_checkpoint(const std::string& filepath) const {
    std::ofstream out(filepath, std::ios::binary);
    if (!out.is_open()) return false;
    out.write(reinterpret_cast<const char*>(lattice_map.data()), chunk_count * sizeof(uint64_t));
    out.write(reinterpret_cast<const char*>(structural_locks.data()), chunk_count * sizeof(uint64_t));
    return true;
}

bool PhaseLattice::import_from_binary_checkpoint(const std::string& filepath) {
    std::ifstream in(filepath, std::ios::binary);
    if (!in.is_open()) return false;
    in.read(reinterpret_cast<char*>(lattice_map.data()), chunk_count * sizeof(uint64_t));
    in.read(reinterpret_cast<char*>(structural_locks.data()), chunk_count * sizeof(uint64_t));
    return true;
}
