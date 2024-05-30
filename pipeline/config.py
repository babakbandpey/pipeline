"""
file: pipeline/config.py
This file contains the configuration for the project.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load all environment variables from the .env file
load_dotenv()

# Access the variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if OPENAI_API_KEY is None:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")

logger.info("OPENAI_API_KEY successfully loaded.")

# Ensure the .env file is not included in version control
# Add the following line to your .gitignore file:
# .env
