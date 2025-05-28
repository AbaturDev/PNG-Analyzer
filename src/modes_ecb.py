import zlib
from chunks import PngChunk
import png_parser


# Computes the CRC checksum for a given PNG chunk
def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = zlib.crc32(check_bytes) & 0xFFFFFFFF
    return crc

def encrypt_chunk_ecb(chunk, image_info, public_key):
    if chunk.type != "IDAT":
        return chunk
    
    if image_info == None:
        raise ValueError("Encryption is not possible without image info")

    # Determine RSA key block size
    n_bits = public_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1
    
    encrypted_data = bytearray()
    decompress_data = zlib.decompress(chunk.data)
    
    raw_pixels = png_parser.remove_png_filters(decompress_data, image_info)
    data = raw_pixels

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

        encrypted_block = c.to_bytes(block_size, byteorder='big')

        encrypted_data.extend(encrypted_block)
    
    filtered_data = png_parser.apply_png_filters(encrypted_data, image_info)

    encrypted_chunk_data = zlib.compress(filtered_data)
    new_crc = compute_crc(chunk.type, encrypted_chunk_data)
    
    return PngChunk(len(encrypted_chunk_data), chunk.type, encrypted_chunk_data, new_crc)

def decrypt_chunk_ecb(chunk, image_info, private_key):
    if chunk.type != "IDAT":
        return chunk
    
    if image_info == None:
        raise ValueError("Decryption is not possible without image info")

    n_bits = private_key[1].bit_length()
    block_size = n_bits // 8
    if n_bits % 8 != 0:
        block_size += 1
   
    chunk_size = block_size - 11  # PKCS#1 v1.5 padding
    
    decompressed_data = zlib.decompress(chunk.data)
    encrypted_pixels = png_parser.remove_png_filters(decompressed_data, image_info)
    
    decrypted_data = bytearray()
    for i in range(0, len(encrypted_pixels), block_size):
        block = encrypted_pixels[i:i+block_size]
        c = int.from_bytes(block, byteorder='big')
        m = pow(c, private_key[0], private_key[1])
        decrypted_block = m.to_bytes(chunk_size, byteorder='big')
        decrypted_data.extend(decrypted_block)
    
    channels = png_parser.get_channels_from_color_type(image_info['color_type'])
    bytes_per_pixel = (channels * image_info['bit_depth'] + 7) // 8
    expected_size = image_info['width'] * image_info['height'] * bytes_per_pixel
    
    decrypted_data = decrypted_data[:expected_size]
    
    filtered_data = png_parser.apply_png_filters(decrypted_data, image_info)
    decrypted_chunk_data = zlib.compress(filtered_data)
    
    new_crc = compute_crc(chunk.type, decrypted_chunk_data)
    return PngChunk(len(decrypted_chunk_data), chunk.type, decrypted_chunk_data, new_crc)

def encrypt_png_ecb(input_path, output_path, public_key):
    chunks = png_parser.read_chunks(input_path)
    
    encrypted_chunks = []
    image_info = None
    for chunk in chunks:
        if chunk.type == "IHDR":
            image_info = png_parser.parse_IHDR(chunk)

        encrypted_chunk = encrypt_chunk_ecb(chunk, image_info, public_key)
        encrypted_chunks.append(encrypted_chunk)
    
    png_parser.write_chunks(output_path, encrypted_chunks)
    print(f"Encrypted with ECB successfully - {output_path}")

def decrypt_png_ecb(input_path, output_path, private_key):
    chunks = png_parser.read_chunks(input_path)
    
    decrypted_chunks = []
    image_info = None
    for chunk in chunks:
        if chunk.type == "IHDR":
            image_info = png_parser.parse_IHDR(chunk)

        decrypted_chunk = decrypt_chunk_ecb(chunk, image_info, private_key)
        decrypted_chunks.append(decrypted_chunk)
    
    png_parser.write_chunks(output_path, decrypted_chunks)
    print(f"Decrypted with ECB successfully - {output_path}")
