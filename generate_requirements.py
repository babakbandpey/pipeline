"""
This script generates a requirements.txt file with
the installed packages in the current environment.
"""
import subprocess

def generate_requirements():
    """
    Generate a requirements.txt file with the installed packages in the current environment.
    """

    # Capture the output of `pip freeze`
    result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, text=True, check=True)
    # Write the output to requirements.txt with UTF-8 encoding (without BOM)
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(result.stdout)

if __name__ == "__main__":
    generate_requirements()
