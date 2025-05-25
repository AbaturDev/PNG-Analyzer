import random
from sympy import isprime

# Computes the greatest common divisor (GCD) of two integers using Euclidean algorithm
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Computes modular inverse using Extended Euclidean Algorithm
# Finds x such that (a * x) % m == 1
def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 % m0

# Generates a random prime number with specified bit length
def generate_prime(bits):
    while True:
        # Generate random odd number with MSB and LSB set to 1
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1    # ensure it's odd and has correct bit length
        if isprime(p):
            return p

# Generates RSA public and private key pair
def generate_keypair(bits = 512):
    # Generate two distinct large primes p and q
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    # Compute RSA modulus n = p * q
    n = p * q

    # Compute Euler's totient φ(n) = (p-1)(q-1)
    phi = (p - 1) * (q - 1)

    # Ensure e is coprime with φ(n)
    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    # Compute private exponent d such that (d * e) % φ(n) = 1
    d = modinv(e, phi)

    return (e, n), (d, n)
