import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

# constants

ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4
KEY_LENGTH = 32 # AES-256
SALT_LENGTH = 16 # std size
NONCE_LENGTH = 12 # std size


# produces 16 random bytes
def generate_salt() -> bytes:
    return os.urandom(SALT_LENGTH)

def derive_key(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode("utf-8"),
        salt = salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=KEY_LENGTH,
        type= Type.ID,
    )

def encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    aesgcm = AESGCM(key) # builds cipher tied to key
    nonce = os.urandom(NONCE_LENGTH) # random no,fresh new
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data = None)
    return nonce , ciphertext

def decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data = None)