"""
file: pipeline/config.py
This file contains the configuration for the project.
"""
import os
import logging
from dotenv import load_dotenv

# Load all environment variables from the .env file
load_dotenv()


# Configure logging
LOGGING_LEVEL = logging.INFO

logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Access the variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if OPENAI_API_KEY is None:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")

logger.info("OPENAI_API_KEY successfully loaded.")

# Ensure the .env file is not included in version control
# Add the following line to your .gitignore file:
# .env
