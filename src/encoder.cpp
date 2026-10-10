#include "pcbl.h"
#include <omp.h>

void PhaseLattice::route_text_prompt(const std::string& prompt) {
    std::vector<uint64_t> generated_signature;
    uint64_t current_chunk = 0;
    
    for (size_t i = 0; i < prompt.length(); ++i) {
        current_chunk = (current_chunk << 8) | static_cast<uint64_t>(static_cast<uint8_t>(prompt[i]));
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

void PhaseLattice::route_image_pixel_stream(const std::vector<uint8_t>& pixel_bytes) {
    std::vector<uint64_t> generated_signature;
    uint64_t current_chunk = 0;
    for (size_t i = 0; i < pixel_bytes.size(); ++i) {
        current_chunk = (current_chunk << 8) | static_cast<uint64_t>(pixel_bytes[i]);
        if (i % 8 == 7 || i == pixel_bytes.size() - 1) {
            current_chunk ^= (current_chunk >> 29);
            current_chunk *= 0x85EBCA6BDB351598ULL;
            generated_signature.push_back(current_chunk);
            current_chunk = 0;
        }
    }
    while (generated_signature.size() < 4) {
        generated_signature.push_back(0x0F0F0F0F0F0F0F0FULL);
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
    
    const std::vector<std::string> global_vocab = {
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "_", "!", ".", " ",
        "ñ", "á", "é", "í", "ó", "ú", "Ñ", "Á", "É", "Í", "Ó", "Ú",
        "А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ",
        "अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ऐ", "ओ", "औ", "क", "ख", "ग", "घ", "च", "छ", "ज", "झ", "त", "थ", "द", "ध", "न", "प", "फ", "ब", "भ", "म", "य", "र", "ल", "व", "श", "स", "ह", "ा", "ि", "ी",
        "அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ", "க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம", "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன", "ா", "ி", "ீ", "ு", "ூ",
        "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ل", "م", "ه", "و", "ي",
        "中", "文", "国", "日", "本", "語", "ハ", "ン", "グ", "ل", "한", "국", "어", "大", "智", "能", "芯", "片", "⚡"
    };
    size_t vocab_size = global_vocab.size();
    
    size_t characters_collected = 0;
    size_t loop_safety_counter = 0;
    
    // Force sampling to continue until we gather the exact number of active characters requested
    while (characters_collected < max_chars && loop_safety_counter < max_chars * 3) {
        size_t matrix_idx = (loop_safety_counter * 13) % chunk_count;
        uint64_t raw_signal = lattice_map[matrix_idx] ^ structural_locks[matrix_idx];
        size_t token_index = (raw_signal ^ (loop_safety_counter * 0x9E3779B9ULL)) % vocab_size;
        
        std::string sampled_char = global_vocab[token_index];
        
        // Skip un-trained raw fallback markers, forcing output density
        if (sampled_char != " " || characters_collected > 0) {
            response += sampled_char;
            characters_collected++;
        }
        loop_safety_counter++;
    }
    return response;
}
