import png_parser
import os


if __name__ == "__main__":
    file_path = os.path.join("assets", "mario.png")

    chunks = png_parser.read_chunks(file_path)
    png_parser.extract_metadata(chunks)

    for chunk in chunks:
        print(chunk)