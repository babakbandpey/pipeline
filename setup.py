"""
The setup.py script is used to package the pipeline module for distribution.
The script reads the requirements.txt file to get the required dependencies and the README.md file
to get the long description of the package.
The setup() function is then called with the necessary parameters to create the package.
"""

from setuptools import setup, find_packages
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_requirements(file_path):
    """
    Read and validate the requirements from a file.
    :param file_path: Path to the requirements file.
    :return: A list of requirements.
    """
    try:
        requirements_path = Path(file_path)
        if requirements_path.is_file():
            with requirements_path.open(encoding='utf-8') as f:
                requirements = f.read().splitlines()
                # Add validation logic here if needed
                return requirements
        else:
            logger.warning("%s not found, proceeding without it.", file_path)
            return []
    except Exception as e:
        logger.error("An error occurred while reading %s: %s", file_path, e)
        return []

def read_long_description(file_path):
    """
    Read and validate the long description from a file.
    :param file_path: Path to the README file.
    :return: The long description as a string.
    """
    try:
        readme_path = Path(file_path)
        if readme_path.is_file():
            with readme_path.open(encoding='utf-8') as f:
                long_description = f.read()
                # Add validation logic here if needed
                return long_description
        else:
            logger.warning("%s not found, proceeding without it.", file_path)
            return ""
    except Exception as e:
        logger.error("An error occurred while reading %s: %s", file_path, e)
        return ""

# Read requirements.txt
required = read_requirements('requirements.txt')

# Read README.md
long_description = read_long_description('README.md')

setup(
    name='pipeline',
    version='0.6',
    packages=find_packages(),
    install_requires=required,
    python_requires='>=3.11',
    author='Babak Bandpey',
    author_email='bb@cocode.dk',
    description='A chatbot pipeline.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/babakbandpey/pipeline',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
