
"""
env_encryptor Module

Description
The env_encryptor module provides functionality to encrypt and decrypt .env files,
ensuring sensitive information such as environment variables are securely managed.
This is achieved through the use of a passphrase and cryptographic techniques to protect the data.

Features

    Key Derivation: Derives cryptographic keys from passphrases using the PBKDF2HMAC algorithm.
    Encryption: Encrypts text data using the derived keys and the Fernet symmetric encryption scheme.
    Decryption: Decrypts encrypted text data using the same passphrase-based key derivation.
    Environment File Processing: Encrypts or decrypts all values in a specified .env file based on user-specified actions.

Functions

    derive_key(passphrase: str, salt: bytes) -> bytes
        Derives a key from the given passphrase and salt using the PBKDF2HMAC algorithm.
        Args:
            passphrase (str): The passphrase used to derive the key.
            salt (bytes): The salt value used in the key derivation.
        Returns: The derived key as bytes.

    encrypt(text: str, passphrase: str) -> str
        Encrypts the given text using the provided passphrase.
        Args:
            text (str): The text to be encrypted.
            passphrase (str): The passphrase used for encryption.
        Returns: The encrypted text as a base64 encoded string.

    decrypt(encrypted_text: str, passphrase: str) -> str
        Decrypts the given encrypted text using the provided passphrase.
        Args:
            encrypted_text (str): The encrypted text to be decrypted.
            passphrase (str): The passphrase used for decryption.
        Returns: The decrypted text.
        Raises: ValueError if the encrypted text is not in a valid format.

    process_env_file(file_path: str, passphrase: str, encrypting: bool)
        Processes the environment file by encrypting or decrypting its values.
        Args:
            file_path (str): The path to the environment file.
            passphrase (str): The passphrase used for encryption or decryption.
            encrypting (bool): True if encrypting, False if decrypting.
        Returns: None.

    main()
        Encrypts or decrypts a .env file based on the specified action.
        Args: None.
        Returns: None.
        Example Usage:
        $ python env_encryptor.py encrypt .env

Usage
To use this module, run the script from the command line,
specifying the action (encrypt or decrypt) and the path to the .env file.
You will be prompted to enter a passphrase to secure the environment variables.

$ python env_encryptor.py [encrypt|decrypt] path/to/.env

Notes

    The first line of the .env file should not contain any environment variable assignments to prevent accidental encryption of non-variable lines.
    Ensure the passphrase is strong and securely stored to avoid unauthorized access to the encrypted data.
"""
import argparse
import base64
import os
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

def derive_key(passphrase: str, salt: bytes) -> bytes:
    """
    Derives a key from the given passphrase and salt using PBKDF2HMAC algorithm.

    Args:
        passphrase (str): The passphrase used to derive the key.
        salt (bytes): The salt value used in the key derivation.

    Returns:
        bytes: The derived key.

    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def encrypt(text: str, passphrase: str) -> str:
    """
    Encrypts the given text using the provided passphrase.

    Args:
        text (str): The text to be encrypted.
        passphrase (str): The passphrase used for encryption.

    Returns:
        str: The encrypted text.
    """
    salt = os.urandom(16)
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    return base64.urlsafe_b64encode(salt + encrypted_text).decode()

def decrypt(encrypted_text: str, passphrase: str) -> str:
    """
    Decrypts the given encrypted text using the provided passphrase.

    Args:
        encrypted_text (str): The encrypted text to be decrypted.
        passphrase (str): The passphrase used for decryption.

    Returns:
        str: The decrypted text.

    Raises:
        ValueError: If the encrypted text is not in a valid format.
    """
    data = base64.urlsafe_b64decode(encrypted_text.encode())
    salt, encrypted_text = data[:16], data[16:]
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text).decode()

def process_env_file(file_path: str, passphrase: str, encrypting: bool):
    """
    Process the environment file by encrypting or decrypting its values.

    Args:
        file_path (str): The path to the environment file.
        passphrase (str): The passphrase used for encryption or decryption.
        encrypting (bool): True if encrypting, False if decrypting.

    Returns:
        None
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(file_path, 'w', encoding='utf-8') as file:
        first_line = lines[0].strip() if lines else ""
        if encrypting and first_line.startswith("#") and "encrypted" in first_line.lower():
            print("Aborting encryption. File is already encrypted.")
            return

        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                if encrypting:
                    new_value = encrypt(value, passphrase)
                else:
                    new_value = decrypt(value, passphrase)
                file.write(f"{key}={new_value}\n")

def main():
    """
    Encrypts or decrypts a .env file based on the specified action.

    The function takes the following command-line arguments:
    - action: The action to perform, either 'encrypt' or 'decrypt'.
    - file: The path to the .env file to be processed.

    The function prompts the user to enter a passphrase for encryption or decryption.
    It then calls the 'process_env_file' function to perform the specified action on the file.
    Finally, it prints a message indicating the completion of the action.

    Example usage:
    $ python env_encryptor.py encrypt .env

    Args:
        None

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Encrypt or decrypt a .env file.')
    parser.add_argument('action', choices=['encrypt', 'decrypt'], help='Action to perform')
    parser.add_argument('file', help='.env file path')

    args = parser.parse_args()
    passphrase = getpass("Enter passphrase: ")

    process_env_file(args.file, passphrase, args.action == 'encrypt')
    print(f"{args.action.capitalize()}ion complete.")

if __name__ == "__main__":
    main()
