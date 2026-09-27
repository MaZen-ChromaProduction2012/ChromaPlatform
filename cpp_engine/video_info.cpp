/**
 * ChromaProduction C++ Engine - Video Inspector Utility
 * Compiles to: video_info
 * Usage: ./video_info <video_file_path>
 */
#include <iostream>
#include <string>
#include <filesystem>
#include <cstdlib>

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <video_file_path>\n";
        return 1;
    }

    std::string video_path = argv[1];
    if (!fs::exists(video_path)) {
        std::cerr << "[-] Video file does not exist: " << video_path << "\n";
        return 2;
    }

    auto file_size = fs::file_size(video_path);
    std::cout << "{\n";
    std::cout << "  \"filename\": \"" << video_path << "\",\n";
    std::cout << "  \"size_bytes\": " << file_size << ",\n";
    std::cout << "  \"size_mb\": " << (file_size / (1024.0 * 1024.0)) << "\n";
    std::cout << "}\n";

    return 0;
}
