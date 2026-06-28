import os
import nacl.secret # cipher scrambles data
import nacl.utils

from argon2.low_level import hash_secret_raw, Type # typed pass -> encryption key

ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4
KEY_LENGTH = nacl.secret.SecretBox.KEY_SIZE
SALT_LENGTH = 16
NONCE_LENGTH = nacl.secret.SecretBox.NONCE_SIZE

# random bytes for different encrpytion keys
def generate_salt() -> bytes:
    return os.urandom(SALT_LENGTH)


def derive_key(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode("utf-8"), # pass -> raw bytes
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=KEY_LENGTH,
        type=Type.ID,
    )


def encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    box = nacl.secret.SecretBox(key)
    # new rand value every call
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    encrypted = box.encrypt(plaintext, nonce)
    return nonce, encrypted.ciphertext

# authenticated decryption
def decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    box = nacl.secret.SecretBox(key)
    return box.decrypt(ciphertext, nonce)
