"""
This file is used to add the pipline directory to the sys.path so that
"""
import sys
import os

# Append the pipeline directory to sys.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
