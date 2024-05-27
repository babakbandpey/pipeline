"""
file: pipeline/config.py
This file contains the configuration for the project.
"""
import os
from dotenv import load_dotenv

# Load all environment variables from the .env file
load_dotenv()

# Access the variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
