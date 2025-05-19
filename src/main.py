import png_parser
import os
from chunks import PngChunk
#import fourier
#from png_anonymizator import anonymize_png
from rsa import generate_keypair
import modes_ebc as ebc


if __name__ == "__main__":
    filename = "sand"
    file_path = os.path.join("assets", f"{filename}.png")
    #output_path = os.path.join("assets", f"{filename}_encrypted.png")

    chunks = png_parser.read_chunks(file_path)

    for chunk in chunks:
        print(chunk)
    
    png_parser.extract_metadata(chunks)

    #fourier.display_fourier_spectrum(file_path)
    #fourier.test_fourier_transformation(file_path)

    # anonymized_file_path = os.path.join("assets", "game_anonymized.png")
    # anonymize_png(file_path, anonymized_file_path)
    # chunks_anonymized = png_parser.read_chunks(anonymized_file_path)

    # for chunk in chunks_anonymized:
    #     print(chunk)

    # png_parser.extract_metadata(chunks_anonymized)

    input_png_file = "assets/sand.png"
    encrypted_png_file = "assets/sand_encrypted.png"
    decrypted_png_file = "assets/sand_decrypted.png"

    public_key, private_key = generate_keypair(bits=512)

    ebc.encrypt_png_ebc(input_png_file, encrypted_png_file, public_key, chunk_types_to_encrypt=["IDAT"])
    print(f"Encrypted PNG: {encrypted_png_file}")

    ebc.decrypt_png_ebc(encrypted_png_file, decrypted_png_file, private_key, chunk_types_to_decrypt=["IDAT"])
    print(f"Decrypted PNG: {decrypted_png_file}")
