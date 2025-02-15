"""
This script checks the encoding of a file.
"""
import os
import argparse
import chardet
from pipeline import logger
from pipeline import FileUtils

def check_encoding(file_path) -> dict:
    """
    Checks the encoding of a file.

    Parameters:
    file_path (str): The path to the file to check.

    Returns:
    dict: A dictionary with the encoding result or an error message.
    """

    result = {}

    if not os.path.isfile(file_path):
        logger.error("Error: The file %s does not exist.", file_path)
        result = {"error": "File not found"}

    try:
        # Check file size to avoid processing excessively large files
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10 MB limit
            logger.error("Error: The file %s is too large to process.", file_path)
            result = {"error": "File too large"}

        with open(file_path, 'rb') as f:
            raw_data = bytearray()
            while chunk := f.read(8192):
                raw_data.extend(chunk)
        result = chardet.detect(raw_data)
    except FileNotFoundError:
        logger.error("Error: The file %s was not found.", file_path)
        result = {"error": "File not found"}
    except PermissionError:
        logger.error("Error: Permission denied for file %s.", file_path)
        result = {"error": "Permission denied"}
    except OSError as e:
        logger.error("OS error occurred: %s", e)
        result = {"error": str(e)}

    return result

def main(files_to_check):
    """ Main function to check the encoding of files. """
    for file_path in files_to_check:
        result = check_encoding(file_path)
        logger.info("%s: %s", file_path, result)

        positions = FileUtils.find_non_ascii_bytes(file_path)
        if positions:
            logger.info("Non-ASCII bytes found in file: %s", file_path)
            logger.info(positions)
            FileUtils.clean_non_ascii_positions(file_path, positions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the encoding of files.")
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='Files to check')
    args = parser.parse_args()
    main(args.files)
