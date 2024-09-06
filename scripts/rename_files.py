import os
import argparse

def replace_spaces_in_name(root_dir):
    # Walk through the directory recursively
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Replace spaces in filenames
        for filename in filenames:
            new_filename = filename.replace(" ", "-")
            if new_filename != filename:
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)
                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {old_file_path} -> {new_file_path}")

        # Replace spaces in directory names
        for dirname in dirnames:
            new_dirname = dirname.replace(" ", "-")
            if new_dirname != dirname:
                old_dir_path = os.path.join(dirpath, dirname)
                new_dir_path = os.path.join(dirpath, new_dirname)
                os.rename(old_dir_path, new_dir_path)
                print(f"Renamed: {old_dir_path} -> {new_dir_path}")

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Recursively rename files and directories by replacing spaces with hyphens.")
    parser.add_argument('--root-directory', required=True, help="The root directory to start renaming files and folders.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the renaming function with the provided root directory
    replace_spaces_in_name(args.root_directory)

    print("Renaming complete.")
