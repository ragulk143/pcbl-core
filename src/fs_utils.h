#ifndef FS_UTILS_H
#define FS_UTILS_H

#include <vector>
#include <string>
#include <filesystem>
#include <iostream>

namespace FSUtils {
    // Crawl a targeted directory and collect paths to all valid raw text files
    inline std::vector<std::string> crawl_directory_for_text(const std::string& folder_path) {
        std::vector<std::string> txt_files;
        try {
            if (std::filesystem::exists(folder_path) && std::filesystem::is_directory(folder_path)) {
                for (const auto& entry : std::filesystem::recursive_directory_iterator(folder_path)) {
                    if (entry.is_regular_file() && entry.path().extension() == ".txt") {
                        txt_files.push_back(entry.path().string());
                    }
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "[FS Error] Directory crawl exception: " << e.what() << std::endl;
        }
        return txt_files;
    }
}

#endif
