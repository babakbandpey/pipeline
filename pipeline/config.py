"""
file: pipeline/config.py
This file contains the configuration for the project.
"""
import os
import base64
from getpass import getpass
import logging

import sys
print(sys.path)


from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load all environment variables from the .env file
load_dotenv()

# Configure logging

OPENAI_API_KEY = None
AZURE_OPENAI_ENDPOINT = None
AZURE_OPENAI_API_KEY_1 = None
LOGGING_LEVEL = logging.INFO

logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def derive_key(passphrase: str, salt: bytes) -> bytes:
    """
    Derive a key from the passphrase and salt.
    params: passphrase: The passphrase to derive the key from.
    params: salt: The salt to use in the key derivation.
    returns: The derived key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def decrypt(encrypted_text: str, passphrase: str) -> str:
    """
    Decrypt the encrypted text using the passphrase.
    params: encrypted_text: The text to decrypt.
    params: passphrase: The passphrase to use for decryption.
    returns: The decrypted text.
    """
    data = base64.urlsafe_b64decode(encrypted_text.encode())
    salt, encrypted_text = data[:16], data[16:]
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    try:
        return fernet.decrypt(encrypted_text).decode()
    except ValueError as e:
        logger.error("Failed to decrypt: %s", str(e))
        return None


def load_env_variable(key, passphrase=None):
    """
    Load an environment variable from the .env file.
    params: key: The key of the environment variable.
    params: passphrase: The passphrase to decrypt the environment variable.
    returns: The value of the environment variable.
    """
    value = os.environ.get(key)
    if passphrase and value:
        return decrypt(value, passphrase)
    return value

def initialize_constants():
    """
    Initialize the constants used in the project.
    """
    global OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY_1
    passphrase = getpass("Enter passphrase to decrypt .env, or 0 if the .env is not encrypted: ")

    if passphrase == '0':
        passphrase = None
        logger.info("The .env file is not encrypted.")
    elif not passphrase:
        logger.error("Passphrase is required to decrypt the .env file.")
        exit()

    OPENAI_API_KEY = load_env_variable('OPENAI_API_KEY', passphrase)
    AZURE_OPENAI_ENDPOINT = load_env_variable('AZURE_OPENAI_ENDPOINT', passphrase)
    AZURE_OPENAI_API_KEY_1 = load_env_variable('AZURE_OPENAI_API_KEY_1', passphrase)

    if OPENAI_API_KEY is None:
        logger.error("OPENAI_API_KEY is not set in the environment variables.")
    else:
        logger.info("OPENAI_API_KEY successfully loaded.")

# Initialize the constants when the module is imported
initialize_constants()

# Ensure the .env file is not included in version control
# Add the following line to your .gitignore file:
# .env
# or encrypt the .env file using the env_encryptor.py script
