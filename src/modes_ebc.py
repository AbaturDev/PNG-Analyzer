from rsa import rsa_decrypt, rsa_encrypt
import png_parser
from chunks import PngChunk
import os
import zlib


def ebc_encrypt(input_file: str, output_file: str, public_key: tuple, chunk_types_to_encrypt: list = ["IDAT"]):
    chunks = png_parser.read_chunks(input_file)
    encrypted_chunks = []

    for chunk in chunks:
        if chunk.type in chunk_types_to_encrypt:
            key_size_bytes = (public_key[1].bit_length() + 7) // 8
            padding_length = key_size_bytes - (len(chunk.data) % key_size_bytes)
            padded_data = chunk.data + b'\0' * padding_length

            encrypted_data = b''
            for i in range(0, len(padded_data), key_size_bytes):
                block = padded_data[i:i + key_size_bytes]
                encrypted_block = rsa_encrypt(block, public_key)
                encrypted_data += encrypted_block

            encrypted_chunks.append(PngChunk(len(encrypted_data), chunk.type, encrypted_data, chunk.crc))
        else:
            encrypted_chunks.append(chunk)

    png_parser.write_chunks(output_file, encrypted_chunks)

def ebc_decrypt(input_file: str, output_file: str, private_key: tuple, chunk_types_to_decrypt: list = ["IDAT"]):
    chunks = png_parser.read_chunks(input_file)
    decrypted_chunks = []

    for chunk in chunks:
        if chunk.type in chunk_types_to_decrypt:
            key_size_bytes = (private_key[1].bit_length() + 7) // 8
            decrypted_data = b''
            for i in range(0, len(chunk.data), key_size_bytes):
                block = chunk.data[i:i + key_size_bytes]
                decrypted_block = rsa_decrypt(block, private_key)
                decrypted_data += decrypted_block
            decrypted_data = decrypted_data.rstrip(b'\0')
            decrypted_chunks.append(PngChunk(len(decrypted_data), chunk.type, decrypted_data, chunk.crc))
        else:
            decrypted_chunks.append(chunk)

    png_parser.write_chunks(output_file, decrypted_chunks)

def encrypt_png_ebc(input_file: str, output_file: str, public_key: tuple, chunk_types_to_encrypt: list = ["IDAT"]):
    chunks = png_parser.read_chunks(input_file)
    encrypted_chunks = []

    for chunk in chunks:
        if chunk.type in chunk_types_to_encrypt:
            iv = os.urandom(16)
            key_size_bytes = (public_key[1].bit_length() + 7) // 8
            padding_length = key_size_bytes - (len(chunk.data) % key_size_bytes)
            padded_data = chunk.data + b'\0' * padding_length
            encrypted_data = iv

            for i in range(0, len(padded_data), key_size_bytes):
                block = padded_data[i:i + key_size_bytes]
                encrypted_block = rsa_encrypt(block, public_key)
                encrypted_data += encrypted_block

            crc = zlib.crc32(chunk.type.encode('ascii') + encrypted_data)
            encrypted_chunks.append(PngChunk(len(encrypted_data), chunk.type, encrypted_data, crc))
        else:
            encrypted_chunks.append(chunk)

    png_parser.write_chunks(output_file, encrypted_chunks)

def decrypt_png_ebc(input_file: str, output_file: str, private_key: tuple, chunk_types_to_decrypt: list = ["IDAT"]):
    chunks = png_parser.read_chunks(input_file)
    decrypted_chunks = []

    for chunk in chunks:
        if chunk.type in chunk_types_to_decrypt:
            key_size_bytes = (private_key[1].bit_length() + 7) // 8
            iv = chunk.data[:16]
            encrypted_data = chunk.data[16:] 

            decrypted_data = b''
            for i in range(0, len(encrypted_data), key_size_bytes):
                block = encrypted_data[i:i + key_size_bytes]
                decrypted_block = rsa_decrypt(block, private_key)
                decrypted_data += decrypted_block

            decrypted_data = decrypted_data.rstrip(b'\0')
            crc = zlib.crc32(chunk.type.encode('ascii') + decrypted_data)
            decrypted_chunks.append(PngChunk(len(decrypted_data), chunk.type, decrypted_data, crc))
        else:
            decrypted_chunks.append(chunk)

    png_parser.write_chunks(output_file, decrypted_chunks)