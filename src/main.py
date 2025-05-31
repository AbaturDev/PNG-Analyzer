import png_parser
import sys
import os
import fourier
from png_anonymizator import anonymize_png
from rsa import generate_keypair
import modes_ecb as ecb
import modes_cbc as cbc
import rsa_lib

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

def ecb_utils(filename, file_path, public_key, private_key):
    encrypted_path = os.path.join("assets", f"{filename}_ecb_encrypted.png")
    decrypted_path = os.path.join("assets", f"{filename}_ecb_decrypted.png")

    ecb.encrypt_png_ecb(file_path, encrypted_path, public_key)

    encrypted_chunks = png_parser.read_chunks(encrypted_path)
    for chunk in encrypted_chunks:
        print(chunk)

    ecb.decrypt_png_ecb(encrypted_path, decrypted_path, private_key)

    decrypted_chunks = png_parser.read_chunks(decrypted_path)
    for chunk in decrypted_chunks:
        print(chunk)

def cbc_utils(filename, file_path, public_key, private_key):
    encrypted_path = os.path.join("assets", f"{filename}_cbc_encrypted.png")
    decrypted_path = os.path.join("assets", f"{filename}_cbc_decrypted.png")

    cbc.encrypt_png_cbc(file_path, encrypted_path, public_key)

    encrypted_chunks = png_parser.read_chunks(encrypted_path)
    for chunk in encrypted_chunks:
        print(chunk)

    cbc.decrypt_png_cbc(encrypted_path, decrypted_path, private_key)

    decrypted_chunks = png_parser.read_chunks(decrypted_path)
    for chunk in decrypted_chunks:
        print(chunk)

def rsa_lib_utils(filename, file_path, public_key, private_key):
    encrypted_path = os.path.join("assets", f"{filename}_rsa_lib_encrypted.png")
    decrypted_path = os.path.join("assets", f"{filename}_rsa_lib_decrypted.png")

    rsa_lib.encrypt_png_rsa_lib(file_path, encrypted_path, public_key)

    encrypted_chunks = png_parser.read_chunks(encrypted_path)
    for chunk in encrypted_chunks:
        print(chunk)

    rsa_lib.decrypt_png_rsa_lib(encrypted_path, decrypted_path, private_key)

    decrypted_chunks = png_parser.read_chunks(decrypted_path)
    for chunk in decrypted_chunks:
        print(chunk)


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Filename argument is missing")
        exit(1)

    filename = sys.argv[1]
    file_path = os.path.join("assets", f"{filename}.png")

    public_key, private_key = generate_keypair(bits=1024)

    chunks = png_parser.read_chunks(file_path)
    for chunk in chunks:
        print(chunk)
    
    #png_parser.extract_metadata(chunks)

    #fourier_utils(file_path)

    #anonymization_utils(filename, file_path)

    ecb_utils(filename, file_path, public_key, private_key)

    #cbc_utils(filename, file_path, public_key, private_key)

    #rsa_lib_utils(filename, file_path, public_key, private_key)