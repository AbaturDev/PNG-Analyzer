import png_parser
import os
import fourier

if __name__ == "__main__":
    file_path = os.path.join("assets", "game.png")

    chunks = png_parser.read_chunks(file_path)

    for chunk in chunks:
        print(chunk)
    
    png_parser.extract_metadata(chunks)

    fourier.display_fourier_spectrum(file_path)
    fourier.test_fourier_transformation(file_path)