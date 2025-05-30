import os
from zlib import crc32
from chunks import PngChunk
import png_parser

# Initialization vector
IV = os.urandom(117)

# Computes CRC for a given PNG chunk type and data
def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = crc32(check_bytes) & 0xffffffff
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
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1

    chunk_size = block_size - 11  # Maximum block size for RSA encryption padding
    data = chunk.data

    # Pad data with null bytes to make it fit full blocks
    if len(data) % chunk_size != 0:
        padding_size = chunk_size - (len(data) % chunk_size)
        data += b'\x00' * padding_size

    encrypted_data = bytearray()
    prev_block = iv  # Start CBC with initial vector

    # Encrypt data
    for i in range(0, len(data), chunk_size):
        block = data[i:i + chunk_size]
        block = xor_bytes(block, prev_block[:chunk_size])  # XOR current block with a previous one or IV (if first iteration)
        m = int.from_bytes(block, byteorder='big')  # Convert block to int
        c = pow(m, public_key[0], public_key[1])  # RSA encryption: c = m^e mod n
        encrypted_block = c.to_bytes(block_size, byteorder='big')  # Convert block back to bytes
        encrypted_data.extend(encrypted_block)
        prev_block = encrypted_block  # Update previous block for next iteration

    new_crc = compute_crc(chunk.type, encrypted_data)
    return PngChunk(length=len(encrypted_data), chunk_type=chunk.type, data=encrypted_data, crc=new_crc)

# Decrypts a single PNG chunk
def decrypt_chunk_cbc(chunk: PngChunk, private_key, iv: bytes) -> PngChunk:
    # Decrypt only IDAT chunks
    if chunk.type != 'IDAT':
        return chunk

    n_bits = private_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1

    data = chunk.data

    # Check if encrypted data is full blocks
    if len(data) % block_size != 0:
        raise ValueError(f"Chunk {chunk.type} has invalid encrypted length")

    decrypted_data = bytearray()
    prev_block = iv
    chunk_size = block_size - 11  # Maximum block size for RSA encryption padding

    # Decrypt data
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        c = int.from_bytes(block, byteorder='big')  # Convert encrypted block to int
        m = pow(c, private_key[0], private_key[1])  # RSA decryption: c^d mod n
        decrypted_block = m.to_bytes(chunk_size, byteorder='big')  # Convert block back to bytes
        decrypted_block = xor_bytes(decrypted_block, prev_block[:chunk_size])  # XOR with a previous block
        decrypted_data.extend(decrypted_block)
        prev_block = block  # Update the previous block for next iteration

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