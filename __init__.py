"""
This file is used to add the project root directory to the sys.path so that
"""
import sys
import os

# Append the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
