import argparse
import base64
import os
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def encrypt(text: str, passphrase: str) -> str:
    salt = os.urandom(16)
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    return base64.urlsafe_b64encode(salt + encrypted_text).decode()

def decrypt(encrypted_text: str, passphrase: str) -> str:
    data = base64.urlsafe_b64decode(encrypted_text.encode())
    salt, encrypted_text = data[:16], data[16:]
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text).decode()

def process_env_file(file_path: str, passphrase: str, encrypting: bool):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                if encrypting:
                    new_value = encrypt(value, passphrase)
                else:
                    new_value = decrypt(value, passphrase)
                file.write(f"{key}={new_value}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Encrypt or decrypt a .env file.')
    parser.add_argument('action', choices=['encrypt', 'decrypt'], help='Action to perform')
    parser.add_argument('file', help='.env file path')

    args = parser.parse_args()
    passphrase = getpass("Enter passphrase: ")

    process_env_file(args.file, passphrase, args.action == 'encrypt')
    print(f"{args.action.capitalize()}ion complete.")
