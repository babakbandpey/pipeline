"""
file: pipeline/config.py
This file contains the configuration for the project.
"""
import os
import logging
from dotenv import load_dotenv

# Load all environment variables from the .env file
load_dotenv()

import os
import base64
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

# Configure logging
LOGGING_LEVEL = logging.INFO

logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def decrypt(encrypted_text: str, passphrase: str) -> str:
    data = base64.urlsafe_b64decode(encrypted_text.encode())
    salt, encrypted_text = data[:16], data[16:]
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    try:
        return fernet.decrypt(encrypted_text).decode()
    except Exception as e:
        logger.error(f"Failed to decrypt: {str(e)}")
        return None


passphrase = getpass("Enter passphrase to decrypt .env: ")

if passphrase is None:
    logger.error("Passphrase is required to decrypt the .env file.")
    exit()

# Access the variables
OPENAI_API_KEY = decrypt(os.environ.get('OPENAI_PLATFORM_API_KEY'), passphrase)
AZURE_OPENAI_ENDPOINT = decrypt(os.environ.get('AZURE_OPENAI_ENDPOINT'), passphrase)
AZURE_OPENAI_API_KEY_1 = decrypt(os.environ.get('AZURE_OPENAI_API_KEY_1'), passphrase)

if OPENAI_API_KEY is None:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")
else:
    logger.info("OPENAI_API_KEY successfully loaded.")

# Ensure the .env file is not included in version control
# Add the following line to your .gitignore file:
# .env
