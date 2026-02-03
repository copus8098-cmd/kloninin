#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
    if(argc < 3) {
        std::cerr << "Usage: pdf_compress <input.pdf> <output.pdf>" << std::endl;
        return 1;
    }

    std::string input = argv[1];
    std::string output = argv[2];

    // QPDF command to compress PDF
    std::string cmd = "qpdf --linearize --compress-streams=y \"" + input + "\" \"" + output + "\"";

    int result = std::system(cmd.c_str());
    if(result == 0){
        std::cout << "Compression done: " << output << std::endl;
    } else {
        std::cerr << "Compression failed" << std::endl;
    }

    return result;
}
