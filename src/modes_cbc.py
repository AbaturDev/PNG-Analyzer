import os
from zlib import crc32
from chunks import PngChunk
import png_parser

IV = os.urandom(117)


def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = crc32(check_bytes) & 0xffffffff
    return crc


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_chunk_cbc(chunk: PngChunk, public_key, iv: bytes) -> PngChunk:
    if chunk.type in ['IHDR', 'IEND']:
        return chunk

    n_bits = public_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1

    chunk_size = block_size - 11
    data = chunk.data
    if len(data) % chunk_size != 0:
        padding_size = chunk_size - (len(data) % chunk_size)
        data += b'\x00' * padding_size

    encrypted_data = bytearray()
    prev_block = iv
    for i in range(0, len(data), chunk_size):
        block = data[i:i + chunk_size]
        block = xor_bytes(block, prev_block[:chunk_size])
        m = int.from_bytes(block, byteorder='big')
        c = pow(m, public_key[0], public_key[1])
        encrypted_block = c.to_bytes(block_size, byteorder='big')
        encrypted_data.extend(encrypted_block)
        prev_block = encrypted_block

    new_crc = compute_crc(chunk.type, encrypted_data)
    return PngChunk(length=len(encrypted_data), chunk_type=chunk.type, data=encrypted_data, crc=new_crc)


def decrypt_chunk_cbc(chunk: PngChunk, private_key, iv: bytes) -> PngChunk:
    if chunk.type in ['IHDR', 'IEND']:
        return chunk

    n_bits = private_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1

    data = chunk.data
    if len(data) % block_size != 0:
        raise ValueError(f"Chunk {chunk.type} has invalid encrypted length")

    decrypted_data = bytearray()
    prev_block = iv
    chunk_size = block_size - 11
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        c = int.from_bytes(block, byteorder='big')
        m = pow(c, private_key[0], private_key[1])
        decrypted_block = m.to_bytes(chunk_size, byteorder='big')
        decrypted_block = xor_bytes(decrypted_block, prev_block[:chunk_size])
        decrypted_data.extend(decrypted_block)
        prev_block = block

    if chunk.type != 'IDAT':
        decrypted_data = decrypted_data.rstrip(b'\x00')
    new_crc = compute_crc(chunk.type, decrypted_data)
    return PngChunk(length=len(decrypted_data), chunk_type=chunk.type, data=decrypted_data, crc=new_crc)

def encrypt_png_cbc(input_path: str, output_path: str, public_key) -> None:
    chunks = png_parser.read_chunks(input_path)

    encrypted_chunks = []
    for chunk in chunks:
        encrypted_chunk = encrypt_chunk_cbc(chunk, public_key, IV)
        encrypted_chunks.append(encrypted_chunk)

    png_parser.write_chunks(output_path, encrypted_chunks)
    print(f"Encrypted with CBC successfully - {output_path}")


def decrypt_png_cbc(input_path: str, output_path: str, private_key) -> None:
    chunks = png_parser.read_chunks(input_path)

    decrypted_chunks = []
    for chunk in chunks:
        decrypted_chunk = decrypt_chunk_cbc(chunk, private_key, IV)
        decrypted_chunks.append(decrypted_chunk)

    png_parser.write_chunks(output_path, decrypted_chunks)
    print(f"Decrypted with CBC successfully - {output_path}")