"""
This script checks the encoding of a file.
"""
import os
import logging
import argparse
import chardet


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_encoding(file_path):
    """
    Checks the encoding of a file.

    Parameters:
    file_path (str): The path to the file to check.

    Returns:
    dict: A dictionary with the encoding result or an error message.
    """
    if not os.path.isfile(file_path):
        logging.error("Error: The file %s does not exist.", file_path)
        return {"error": "File not found"}

    try:
        # Check file size to avoid processing excessively large files
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10 MB limit
            logging.error("Error: The file %s is too large to process.", file_path)
            return {"error": "File too large"}

        with open(file_path, 'rb') as f:
            raw_data = bytearray()
            while chunk := f.read(8192):
                raw_data.extend(chunk)
        return chardet.detect(raw_data)
    except FileNotFoundError:
        logging.error("Error: The file %s was not found.", file_path)
        return {"error": "File not found"}
    except PermissionError:
        logging.error("Error: Permission denied for file %s.", file_path)
        return {"error": "Permission denied"}
    except OSError as e:
        logging.error("OS error occurred: %s", e)
        return {"error": str(e)}
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return {"error": str(e)}

def main(files_to_check):
    for file_path in files_to_check:
        result = check_encoding(file_path)
        logging.info("%s: %s", file_path, result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the encoding of files.")
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='Files to check')
    args = parser.parse_args()
    main(args.files)
