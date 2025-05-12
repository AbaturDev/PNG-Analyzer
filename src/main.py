import png_parser
import os
#import fourier
#from png_anonymizator import anonymize_png
from rsa import generate_keypair
import modes_ebc as ebc

if __name__ == "__main__":
    file_path = os.path.join("assets", "game.png")

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

    public_key, private_key = generate_keypair(512)

    idat_data = b"".join(chunk.data for chunk in chunks if chunk.type == b'IDAT')

    encrypted_idat = ebc.encrypt_ecb(idat_data, public_key)

    # 4. Zamień dane IDAT w oryginalnych chunkach na zaszyfrowane
    encrypted_chunks = []
    encrypted_offset = 0
    for chunk in chunks:
        if chunk.type == b'IDAT':
            length = len(chunk.data)
            new_data = encrypted_idat[encrypted_offset:encrypted_offset+length]
            encrypted_chunks.append({
                'length': length,
                'type': chunk.type,
                'data': new_data
            })
            encrypted_offset += length
        else:
            encrypted_chunks.append(chunk)

    # 5. Zapisz nowy plik PNG z zaszyfrowaną masą bitową
    encrypted_path = os.path.join("assets", "game_encrypted.png")
    png_parser.write_chunks(encrypted_path, encrypted_chunks)
    print("\n📁 Zaszyfrowany plik zapisano jako:", encrypted_path)

    # 6. (opcjonalnie) odszyfruj z powrotem i sprawdź poprawność
    chunks_enc = png_parser.read_chunks(encrypted_path)
    idat_enc = b"".join(chunk.data for chunk in chunks_enc if chunk.type == b'IDAT')
    decrypted_idat = ebc.decrypt_ecb(idat_enc, private_key)

    decrypted_chunks = []
    decrypted_offset = 0
    for chunk in chunks_enc:
        if chunk.type == b'IDAT':
            length = len(chunk.data)
            new_data = decrypted_idat[decrypted_offset:decrypted_offset+length]
            decrypted_chunks.append({
                'length': length,
                'type': chunk.type,
                'data': new_data
            })
            decrypted_offset += length
        else:
            decrypted_chunks.append(chunk)

    decrypted_path = os.path.join("assets", "game_decrypted.png")
    png_parser.write_chunks(decrypted_path, decrypted_chunks)
    print("🔓 Odszyfrowany plik zapisano jako:", decrypted_path)