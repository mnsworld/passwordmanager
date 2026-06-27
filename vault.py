import json
import os
import crypto_core as cc

VAULT_PATH = os.path.join(os.path.expanduser('~'), ".local_passmgr_vault.dat")

# custom exception

class WrongPasswordError(Exception):
    pass

def vault_exists() -> bool:
    return os.path.exists(VAULT_PATH)

def create_vault(master_password: str) -> None:
    salt = cc.generate_salt()
    key = cc.derive_key(master_password, salt)
    empty_entries =[]
    _write_vault(salt, key, empty_entries)


def _write_vault(salt: bytes, key: bytes, entries: list) -> None:
    plaintext = json.dumps(entries).encode("utf-8")
    nonce, ciphertext = cc.encrypt(key, plaintext)

    with open (VAULT_PATH, "wb") as f:
        f.write(salt)
        f.write(nonce)
        f.write(ciphertext)

    try:
        os.chmod(VAULT_PATH, 0o600)
    except (NotImplementedError, OSError):
        pass

    # decrypting the files backing into entries

def load_vault(master_password: str) -> list[dict]:
    with open(VAULT_PATH, "rb") as f:
        raw = f.read()

    salt = raw[:cc.SALT_LENGTH]
    nonce = raw[cc.SALT_LENGTH:cc.SALT_LENGTH + cc.NONCE_LENGTH:]
    ciphertext = raw[cc.SALT_LENGTH + cc.NONCE_LENGTH:]


    key = cc.derive_key(master_password, salt)

    try:
        plaintext = cc.decrypt(key, nonce, ciphertext)
    except Exception:
        raise WrongPasswordError("invalid password, or vault file is corrupted.")

    entries = json.loads(plaintext.decode("utf-8"))
    return entries


# re-encrypting after changes

def save_vault(master_password: str, entries: list[dict]) -> None:
    salt = cc.generate_salt()
    key = cc.derive_key(master_password, salt)
    _write_vault(salt, key, entries)

