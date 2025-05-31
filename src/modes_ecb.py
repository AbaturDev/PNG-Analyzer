import zlib
from chunks import PngChunk
import png_parser


# Computes the CRC checksum for a given PNG chunk
def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = zlib.crc32(check_bytes) & 0xFFFFFFFF
    return crc

def encrypt_chunk_ecb(chunk, public_key):
    if chunk.type != "IDAT":
        return chunk
    
    # Determine RSA key block size
    n_bits = public_key[1].bit_length()
    block_size = n_bits // 8 - 1
    
    encrypted_data = bytearray()
    data = zlib.decompress(chunk.data)
    
    # Encrypt each plaintext block
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        m = int.from_bytes(block, byteorder='big')
        c = pow(m, public_key[0], public_key[1])

        encrypted_block = c.to_bytes(block_size+1, byteorder='big')

        encrypted_data.extend(encrypted_block)
    
    encrypted_chunk_data = zlib.compress(encrypted_data)
    new_crc = compute_crc(chunk.type, encrypted_chunk_data)
    
    return PngChunk(len(encrypted_chunk_data), chunk.type, encrypted_chunk_data, new_crc)

def decrypt_chunk_ecb(chunk, private_key):
    if chunk.type != "IDAT":
        return chunk
    
    n_bits = private_key[1].bit_length()
    block_size = n_bits // 8
    
    data = zlib.decompress(chunk.data)
    
    decrypted_data = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        c = int.from_bytes(block, byteorder='big')
        m = pow(c, private_key[0], private_key[1])
        decrypted_block = m.to_bytes(block_size-1, byteorder='big')
        decrypted_data.extend(decrypted_block)
    
    decrypted_chunk_data = zlib.compress(decrypted_data)
    
    new_crc = compute_crc(chunk.type, decrypted_chunk_data)
    return PngChunk(len(decrypted_chunk_data), chunk.type, decrypted_chunk_data, new_crc)

def encrypt_png_ecb(input_path, output_path, public_key):
    chunks = png_parser.read_chunks(input_path)
    
    encrypted_chunks = []
    for chunk in chunks:
        encrypted_chunk = encrypt_chunk_ecb(chunk, public_key)
        encrypted_chunks.append(encrypted_chunk)
    
    png_parser.write_chunks(output_path, encrypted_chunks)
    print(f"Encrypted with ECB successfully - {output_path}")

def decrypt_png_ecb(input_path, output_path, private_key):
    chunks = png_parser.read_chunks(input_path)
    
    decrypted_chunks = []
    for chunk in chunks:
        decrypted_chunk = decrypt_chunk_ecb(chunk, private_key)
        decrypted_chunks.append(decrypted_chunk)
    
    png_parser.write_chunks(output_path, decrypted_chunks)
    print(f"Decrypted with ECB successfully - {output_path}")
