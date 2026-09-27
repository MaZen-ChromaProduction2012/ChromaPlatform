/**
 * ChromaProduction C++ Engine - Fast Folder Compression Utility
 * Compiles to: compress
 * Usage: ./compress <input_path> <output_zip_path>
 */
#include <iostream>
#include <string>
#include <filesystem>
#include <cstdlib>

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <input_path> <output_zip_path>\n";
        return 1;
    }

    std::string input_path = argv[1];
    std::string output_zip = argv[2];

    if (!fs::exists(input_path)) {
        std::cerr << "[-] Input path does not exist: " << input_path << "\n";
        return 2;
    }

    std::cout << "[+] Chroma C++ Compressor: Packing " << input_path << " into " << output_zip << "...\n";

    std::string cmd = "zip -r -q \"" + output_zip + "\" \"" + input_path + "\"";
    int ret = std::system(cmd.c_str());

    if (ret == 0) {
        std::cout << "[+] Successfully compressed archive: " << output_zip << "\n";
        return 0;
    } else {
        std::cerr << "[-] Compression command failed with code: " << ret << "\n";
        return ret;
    }
}
