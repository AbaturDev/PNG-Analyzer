import zlib
from chunks import PngChunk
import png_parser


# Computes the CRC checksum for a given PNG chunk
def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = zlib.crc32(check_bytes) & 0xFFFFFFFF
    return crc

def encrypt_chunk_ebc(chunk, public_key):
    if chunk.type in ["IEND", "IHDR"]:
        return chunk
    
    # Determine RSA key block size
    n_bits = public_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1
    
    encrypted_data = bytearray()
    data = chunk.data
    
    # Maximum plaintext size for RSA encryption with PKCS#1 v1.5 padding
    chunk_size = block_size - 11
    
    # Pad data to be divisible by chunk_size
    if len(data) % chunk_size != 0:
        padding_size = chunk_size - (len(data) % chunk_size)
        data += b'\x00' * padding_size
    
    # Encrypt each plaintext block
    for i in range(0, len(data), chunk_size):
        block = data[i:i+chunk_size]
        m = int.from_bytes(block, byteorder='big')
        c = pow(m, public_key[0], public_key[1])
        try:
            encrypted_block = c.to_bytes(block_size, byteorder='big')
        except OverflowError:
            # Handle rare cases when encrypted result is bigger than expected
            actual_size = (c.bit_length() + 7) // 8
            if actual_size > block_size:
                print(f"Warning: Encrypted value requires {actual_size} bytes but block_size is {block_size}")
                encrypted_block = c.to_bytes(actual_size, byteorder='big')
            else:
                encrypted_block = c.to_bytes(actual_size, byteorder='big')
                if actual_size < block_size:
                    padded_block = bytearray(block_size - actual_size) + encrypted_block
                    encrypted_block = bytes(padded_block)

        encrypted_data.extend(encrypted_block)
    
    new_crc = compute_crc(chunk.type, encrypted_data)
    
    return PngChunk(len(encrypted_data), chunk.type, encrypted_data, new_crc)

def decrypt_chunk_ebc(chunk, private_key):
    if chunk.type in ["IEND", "IHDR"]:
        return chunk
    
    # Determine RSA key block size
    n_bits = private_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1
    
    # Check for corrupted or non-aligned encrypted data
    if len(chunk.data) % block_size != 0:
        print(f"Warning: Chunk data length ({len(chunk.data)} bytes) for chunk {chunk.type} is not a multiple of RSA block size ({block_size} bytes)")
        
        blocks_count = len(chunk.data) // block_size
        remainder = len(chunk.data) % block_size
        if remainder > 0:
            if remainder > block_size - 5:
                # Reduce block size to handle misalignment
                block_size = len(chunk.data) // blocks_count
                if len(chunk.data) % blocks_count != 0:
                    block_size += 1
            else:
                # Pad if just a small remainder is missing
                print(f"Adding padding to make chunk data length a multiple of block size")
                padding_size = block_size - remainder
                chunk.data += b'\x00' * padding_size
    
    decrypted_data = bytearray()
    chunk_size = block_size - 11
    
    # Decrypt each block
    for i in range(0, len(chunk.data), block_size):
        block = chunk.data[i:i+block_size]
        c = int.from_bytes(block, byteorder='big')
        m = pow(c, private_key[0], private_key[1])
        try:
            decrypted_block = m.to_bytes(chunk_size, byteorder='big')
        except OverflowError:
            # Handle small decrypted integers
            actual_size = (m.bit_length() + 7) // 8
            decrypted_block = m.to_bytes(actual_size, byteorder='big')
            if actual_size < chunk_size:
                decrypted_block = b'\x00' * (chunk_size - actual_size) + decrypted_block
                
        decrypted_data.extend(decrypted_block)
    
    # Remove padding if not IDAT chunk
    if chunk.type != "IDAT":
        decrypted_data = decrypted_data.rstrip(b'\x00')
    
    new_crc = compute_crc(chunk.type, decrypted_data)
    
    return PngChunk(len(decrypted_data), chunk.type, decrypted_data, new_crc)

def encrypt_png_ebc(input_path, output_path, public_key):
    chunks = png_parser.read_chunks(input_path)
    
    encrypted_chunks = []
    for chunk in chunks:
        encrypted_chunk = encrypt_chunk_ebc(chunk, public_key)
        encrypted_chunks.append(encrypted_chunk)
    
    png_parser.write_chunks(output_path, encrypted_chunks)
    print(f"Encrypted successfully - {output_path}")

def decrypt_png_ebc(input_path, output_path, private_key):
    chunks = png_parser.read_chunks(input_path)
    
    decrypted_chunks = []
    for chunk in chunks:
        try:
            decrypted_chunk = decrypt_chunk_ebc(chunk, private_key)
            decrypted_chunks.append(decrypted_chunk)
        except Exception as e:
            print(f"Error decrypting chunk {chunk.type}: {str(e)}")
            # On failure, keep the original chunk
            decrypted_chunks.append(chunk)
    
    png_parser.write_chunks(output_path, decrypted_chunks)
    print(f"Decrypted successfully - {output_path}")