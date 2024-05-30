"""
This script generates a requirements.txt file with
the installed packages in the current environment.
"""
import subprocess
import os
import logging
from contextlib import contextmanager
from typing import Optional

@contextmanager
def setup_logging(level=logging.INFO):
    """
    Context manager to set up logging configuration.
    """
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        yield
    finally:
        logging.shutdown()


def generate_requirements(
        file_path: str = 'requirements.txt',
        overwrite: bool = True,
        pip_cmd: str = 'pip'
        ) -> None:
    """
    Generate a requirements.txt file with the installed packages in the current environment.

    :param file_path: The path to the requirements file.
    :param overwrite: Whether to overwrite the file if it exists.
    :param pip_cmd: The pip command to use (default is 'pip').
    """
    try:
        # Capture the output of `pip freeze`
        result = subprocess.run([pip_cmd, 'freeze'], stdout=subprocess.PIPE, text=True, check=True)

        # Check if the file already exists
        if os.path.exists(file_path):
            if not overwrite:
                logging.warning("%s already exists. Use overwrite=True to overwrite the file.", file_path)
                return
            logging.info("%s already exists and will be overwritten.", file_path)

        # Write the output to the file with UTF-8 encoding (without BOM)
        temp_file_path = f"{file_path}.tmp"
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        os.replace(temp_file_path, file_path)
        logging.info("Requirements have been written to %s.", file_path)

    except subprocess.CalledProcessError as e:
        logging.error("An error occurred while running %s freeze: %s", pip_cmd, e)
    except IOError as e:
        logging.error("An error occurred while writing to %s: %s", file_path, e)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)

if __name__ == "__main__":
    with setup_logging():
        generate_requirements()
