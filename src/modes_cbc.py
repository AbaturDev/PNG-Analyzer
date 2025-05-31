import os
import zlib
from chunks import PngChunk
import png_parser

# Initialization vector
IV = os.urandom(255)

# Computes CRC for a given PNG chunk type and data
def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = zlib.crc32(check_bytes) & 0xffffffff
    return crc

# XORs two byte sequences
def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

# Encrypts a single PNG chunk
def encrypt_chunk_cbc(chunk: PngChunk, public_key, iv: bytes) -> PngChunk:
    # Encrypt only IDAT chunks
    if chunk.type != 'IDAT':
        return chunk

    # Determine block size from RSA modulus
    n_bits = public_key[1].bit_length()
    block_size = n_bits // 8 - 1

    data = zlib.decompress(chunk.data)
    encrypted_data = bytearray()
    prev_block = iv  # Start CBC with initial vector

    # Encrypt data
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        block = xor_bytes(block, prev_block[:block_size])  # XOR current block with a previous one or IV (if first iteration)
        m = int.from_bytes(block, byteorder='big')  # Convert block to int
        c = pow(m, public_key[0], public_key[1])  # RSA encryption: c = m^e mod n
        encrypted_block = c.to_bytes(block_size + 1, byteorder='big')  # Convert block back to bytes
        encrypted_data.extend(encrypted_block)
        prev_block = encrypted_block  # Update previous block for next iteration

    encrypted_data = zlib.compress(encrypted_data)
    new_crc = compute_crc(chunk.type, encrypted_data)
    return PngChunk(length=len(encrypted_data), chunk_type=chunk.type, data=encrypted_data, crc=new_crc)

# Decrypts a single PNG chunk
def decrypt_chunk_cbc(chunk: PngChunk, private_key, iv: bytes) -> PngChunk:
    # Decrypt only IDAT chunks
    if chunk.type != 'IDAT':
        return chunk

    n_bits = private_key[1].bit_length()
    block_size = n_bits // 8 - 1

    data = zlib.decompress(chunk.data)
    decrypted_data = bytearray()
    prev_block = iv

    # Decrypt data
    for i in range(0, len(data), block_size + 1):
        block = data[i:i + block_size + 1]
        c = int.from_bytes(block, byteorder='big')  # Convert encrypted block to int
        m = pow(c, private_key[0], private_key[1])  # RSA decryption: c^d mod n
        decrypted_block = m.to_bytes(block_size, byteorder='big')  # Convert block back to bytes
        decrypted_block = xor_bytes(decrypted_block, prev_block[:block_size + 1])  # XOR with a previous block
        decrypted_data.extend(decrypted_block)
        prev_block = block  # Update the previous block for next iteration

    decrypted_data = zlib.compress(decrypted_data)
    new_crc = compute_crc(chunk.type, decrypted_data)
    return PngChunk(length=len(decrypted_data), chunk_type=chunk.type, data=decrypted_data, crc=new_crc)

# Encrypt PNG file
def encrypt_png_cbc(input_path: str, output_path: str, public_key) -> None:
    chunks = png_parser.read_chunks(input_path)

    encrypted_chunks = []
    for chunk in chunks:
        encrypted_chunk = encrypt_chunk_cbc(chunk, public_key, IV)
        encrypted_chunks.append(encrypted_chunk)

    png_parser.write_chunks(output_path, encrypted_chunks)
    print(f"Encrypted with CBC successfully - {output_path}")

# Decrypt PNG file
def decrypt_png_cbc(input_path: str, output_path: str, private_key) -> None:
    chunks = png_parser.read_chunks(input_path)

    decrypted_chunks = []
    for chunk in chunks:
        decrypted_chunk = decrypt_chunk_cbc(chunk, private_key, IV)
        decrypted_chunks.append(decrypted_chunk)

    png_parser.write_chunks(output_path, decrypted_chunks)
    print(f"Decrypted with CBC successfully - {output_path}")