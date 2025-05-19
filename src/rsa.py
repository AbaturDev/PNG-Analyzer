import random
from sympy import isprime


def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a

def modinv(a: int, m: int) -> int:
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 % m0

def generate_prime(bits: int) -> int:
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1
        if isprime(p):
            return p

def generate_keypair(bits: int = 512):
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    d = modinv(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(message: bytes, public_key: tuple) -> bytes:
    e, n = public_key
    m = int.from_bytes(message, 'big')
    c = pow(m, e, n)
    return c.to_bytes((c.bit_length() + 7) // 8, 'big')

def rsa_decrypt(ciphertext: bytes, private_key: tuple) -> bytes:
    d, n = private_key
    c = int.from_bytes(ciphertext, 'big')
    m = pow(c, d, n)
    return m.to_bytes((m.bit_length() + 7) // 8, 'big')