"""
file ./setup.py
This file contains the setup configuration for the project.
"""
from setuptools import setup, find_packages

with open('requirements.txt', encoding='utf-8') as f:
    required = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pipeline',
    version='0.1.0',
    packages=find_packages(),
    install_requires=required,
    python_requires='>=3.11',
    author='Babak Bandpey',
    author_email='bb@cocode.dk',
    description='A chatbot pipeline.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/babakbandpey/pipeline',
)
