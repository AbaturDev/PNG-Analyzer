def chunk_data(data: bytes, chunk_size: int) -> list[bytes]:
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

def encrypt_ecb(data: bytes, key: tuple[int, int]) -> bytes:
    e, n = key
    block_size = (n.bit_length() - 1) // 8
    encrypted = []

    for block in chunk_data(data, block_size):
        m = int.from_bytes(block, byteorder='big')
        c = pow(m, e, n)
        encrypted_block = c.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
        encrypted.append(encrypted_block)

    return b"".join(encrypted)

def decrypt_ecb(data: bytes, key: tuple[int, int]) -> bytes:
    d, n = key
    block_size = (n.bit_length() + 7) // 8
    decrypted = []

    for block in chunk_data(data, block_size):
        c = int.from_bytes(block, byteorder='big')
        m = pow(c, d, n)
        decrypted_block = m.to_bytes((n.bit_length() - 1) // 8, byteorder='big')
        decrypted.append(decrypted_block)

    return b"".join(decrypted)