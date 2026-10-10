#include <iostream>
#include <vector>
#include <chrono>
#include <fstream>
#include <string>
#include <filesystem>
#include "lattice.h"

int main() {
    std::cout << "[PCBL Suite V1.9] Initializing Massive Core Code Ingestion Pass..." << std::endl;
    size_t num_elements = 2000000000;
    PhaseLattice engine(num_elements);

    std::string target_dir = "hacker_knowledge_base";
    std::filesystem::create_directory(target_dir);

    // Dynamic Bootstrap Hack: Copy your engine's actual raw source files into the dataset folder!
    // This feeds the lattice thousands of words of real programming structures and syntax.
    try {
        std::filesystem::copy_file("../src/lattice.cpp", target_dir + "/heavy_code_lattice.txt", std::filesystem::copy_options::overwrite_existing);
        std::filesystem::copy_file("../src/main.cpp", target_dir + "/heavy_code_main.txt", std::filesystem::copy_options::overwrite_existing);
        std::cout << "[Bootstrap] Successfully imported large core source code files into dataset." << std::endl;
    } catch (const std::exception& e) {
        std::cout << "[Bootstrap Warning] Using existing folder assets: " << e.what() << std::endl;
    }

    std::vector<uint64_t> target_goal = {0xDECAFFADDECAFFADULL, 0x1122334455667788ULL};

    std::cout << "\n[Epoch Loop] Launching 5-Pass Heavy Code Learning Pass..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    for (int epoch = 1; epoch <= 5; ++epoch) {
        engine.ingest_entire_directory(target_dir, target_goal);
        std::cout << ">>> [Epoch " << epoch << "] Parameter Lock Convergence: " 
                  << engine.calculate_lock_percentage() << " %\n" << std::endl;
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;

    std::cout << "[Execution Complete] Processed heavy code datasets in: " 
              << elapsed.count() << " ms" << std::endl;

    // Run inference pass to check syntax reaction
    std::string prompt = "void_PhaseLattice_forward_token_routing";
    std::string output = engine.generate_response_string(prompt, 50);
    std::cout << "\n[Generative Pass] Output Tokens: \"" << output << "\"" << std::endl;

    return 0;
}
