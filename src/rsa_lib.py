from zlib import crc32
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Random import get_random_bytes
from chunks import PngChunk
import png_parser

# Computes CRC for a given PNG chunk type and data
def compute_crc(chunk_type, data):
    check_bytes = chunk_type.encode('ascii') + data
    crc = crc32(check_bytes) & 0xFFFFFFFF
    return crc

# Encrypt a single PNG chunk using RSA PKCS#1 v1.5 encryption
def encrypt_chunk_rsa_lib(chunk: PngChunk, public_key) -> PngChunk:
    # Encrypt only IDAT chunks
    if chunk.type != 'IDAT':
        return chunk

    e, n = public_key
    rsa_key = RSA.construct((n, e))  # Construct RSA-key from public key
    cipher = PKCS1_v1_5.new(rsa_key)  # Init PKCS#1 v1.5 encryption cipher

    block_size = rsa_key.size_in_bytes()  # RSA block size (in bytes)
    chunk_size = block_size - 11  # Maximum block size for RSA encryption padding
    data = chunk.data
    encrypted_data = bytearray()

    # Encrypt data
    for i in range(0, len(data), chunk_size):
        block = data[i:i + chunk_size]
        encrypted_block = cipher.encrypt(block)  # Encrypt using the RSA cipher
        encrypted_data.extend(encrypted_block)

    new_crc = compute_crc(chunk.type, encrypted_data)
    return PngChunk(length=len(encrypted_data),chunk_type=chunk.type, data=encrypted_data, crc=new_crc)

# Decrypts a single PNG chunk using the RSA PKCS#1 v1.5 decryption mode
def decrypt_chunk_rsa_lib(chunk: PngChunk, private_key) -> PngChunk:
    # Decrypt only IDAT  chunks
    if chunk.type != 'IDAT':
        return chunk

    d, n = private_key
    e = 65537  # Exponent used in rsa.py
    rsa_key = RSA.construct((n, e, d))  # Construct RSA-key from private key
    cipher = PKCS1_v1_5.new(rsa_key)  # Init PKCS#1 v1.5 decryption cipher

    block_size = rsa_key.size_in_bytes()  # RSA block size (in bytes)
    sentinel = get_random_bytes(8)  # Used to detect decryption failure
    decrypted_data = bytearray()
    data = chunk.data

    # Decrypt data
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        decrypted_block = cipher.decrypt(block, sentinel)  # Decrypt using the RSA cipher with sentinel to detect decryption failure
        decrypted_data.extend(decrypted_block)

    new_crc = compute_crc(chunk.type, decrypted_data)
    return PngChunk(length=len(decrypted_data), chunk_type=chunk.type, data=decrypted_data, crc=new_crc)

# Encrypt PNG file using RSA library
def encrypt_png_rsa_lib(input_path: str, output_path: str, public_key) -> None:
    chunks = png_parser.read_chunks(input_path)

    encrypted_chunks = []
    for chunk in chunks:
        encrypted_chunk = encrypt_chunk_rsa_lib(chunk, public_key)
        encrypted_chunks.append(encrypted_chunk)

    png_parser.write_chunks(output_path, encrypted_chunks)
    print(f"Encrypted with RSA library successfully - {output_path}")

# Decrypt PNG file using RSA library
def decrypt_png_rsa_lib(input_path: str, output_path: str, private_key) -> None:
    chunks = png_parser.read_chunks(input_path)

    decrypted_chunks = []
    for chunk in chunks:
        decrypted_chunk = decrypt_chunk_rsa_lib(chunk, private_key)
        decrypted_chunks.append(decrypted_chunk)

    png_parser.write_chunks(output_path, decrypted_chunks)
    print(f"Decrypted with RSA library successfully - {output_path}")