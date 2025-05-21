import png_parser
import sys
import os
from chunks import PngChunk
import fourier
from png_anonymizator import anonymize_png
from rsa import generate_keypair
import modes_ebc as ebc

def fourier_utils(file_path):
    fourier.display_fourier_spectrum(file_path)
    fourier.test_fourier_transformation(file_path)


def anonymization_utils(filename ,file_path):
    anonymized_file_path = os.path.join("assets", f"{filename}_anonymized.png")

    anonymize_png(file_path, anonymized_file_path)
    chunks_anonymized = png_parser.read_chunks(anonymized_file_path)

    for chunk in chunks_anonymized:
        print(chunk)

    png_parser.extract_metadata(chunks_anonymized)


def ebc_utils(filename, file_path, public_key, private_key):
    encrypted_path = os.path.join("assets", f"{filename}_ebc_encrypted.png")
    decrypted_path = os.path.join("assets", f"{filename}_ebc_decrypted.png")

    ebc.encrypt_png_ebc(file_path, encrypted_path, public_key)

    encrypted_chunks = png_parser.read_chunks(encrypted_path)
    for chunk in encrypted_chunks:
        print(chunk)

    try:
        png_parser.extract_metadata(encrypted_chunks)
    except Exception as e:
        print(f"Failed to read metadata: {e}")

    ebc.decrypt_png_ebc(encrypted_path, decrypted_path, private_key)

    decrypted_chunks = png_parser.read_chunks(decrypted_path)
    for chunk in decrypted_chunks:
        print(chunk)
    
    try:
        png_parser.extract_metadata(decrypted_chunks)
    except Exception as e:
        print(f"Failed to read metadata: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Filename argument is missing")
        exit(1)

    filename = sys.argv[1]
    file_path = os.path.join("assets", f"{filename}.png")

    public_key, private_key = generate_keypair(bits=512)

    chunks = png_parser.read_chunks(file_path)
    for chunk in chunks:
       print(chunk)
    
    png_parser.extract_metadata(chunks)

    fourier_utils(file_path)

    anonymization_utils(filename, file_path)

    ebc_utils(filename, file_path, public_key, private_key)
