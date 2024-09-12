import subprocess
import os
import logging
import platform

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler to save logs to push.log
file_handler = logging.FileHandler('./logs/push.log')
file_handler.setLevel(logging.INFO)

# Create console handler to print logs to stdout
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define the log format
formatter = logging.Formatter('>>>> %(filename)s - %(lineno)d - %(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def run_command(command, interactive=False):
    """
    Run a shell command and return the output.
    params: command: The command to run.
    params: interactive: Whether the command is interactive (default: False).
    returns: The stdout and stderr output of the command.
    """
    try:
        logger.info(f"Running command: {command}")
        if interactive:
            result = subprocess.run(command, shell=True, check=True)
            logger.info(result.stdout.decode() if result.stdout else "No stdout output")
        else:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            stdout_output = result.stdout.decode().strip()
            stderr_output = result.stderr.decode().strip()

            logger.info(f"Stdout: {stdout_output}")
            logger.info(f"Stderr: {stderr_output if stderr_output else 'No stderr output'}")
            return stdout_output, stderr_output
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {command}")
        logger.error(e.stderr.decode() if e.stderr else "No stderr output")
        exit(1)


def check_file_exists(file_path):
    """
    Check if the specified file exists.
    params: file_path: The path to the file to check.
    """
    if not os.path.isfile(file_path):
        logger.error(f"Expected file {file_path} not found.")
        raise FileNotFoundError(f"File not found: {file_path}")


def check_if_running_in_docker():
    """
    Check if the script is running in a Docker container.
    """
    if platform.system() == 'Linux':
        if os.path.exists('/.dockerenv'):
            logger.error("This script should not be executed from within a Docker container.")
            exit(1)
        try:
            with open('/proc/1/cmdline', 'r') as f:
                if 'docker' in f.read():
                    logger.error("This script should not be executed from within a Docker container.")
                    exit(1)
        except FileNotFoundError:
            pass
    else:
        logger.info("Docker environment check skipped for non-Linux platform.")


def add_ssh_key(ssh_id='id_rsa'):
    """
    Add the specified SSH key to the ssh-agent.
    params: ssh_id: The SSH key identifier (default: id_rsa).
    """
    ssh_key_path = os.path.expanduser(f"~/.ssh/{ssh_id}")
    if not os.path.isfile(ssh_key_path):
        logger.error(f"SSH key not found at {ssh_key_path}. Please ensure it exists.")
        exit(1)

    try:
        if platform.system() == 'Windows':
            # Windows-specific command to start ssh-agent and add key
            run_command("start-ssh-agent.cmd")
            run_command(f"ssh-add '{ssh_key_path}'", interactive=True)
        else:
            # Unix-like systems
            run_command("eval $(ssh-agent -s)", interactive=True)
            run_command(f"ssh-add {ssh_key_path}", interactive=True)
        logger.info(f"SSH key {ssh_key_path} added to the ssh-agent.")
    except Exception as e:
        logger.error("Error adding SSH key to the ssh-agent.")
        logger.error(str(e))
        exit(1)


def activate_virtualenv_and_run_script(container_id, shell_type="bash"):
    """
    Activate the virtual environment and run the commit_message.py script inside the container.
    params: container_id: The ID of the Docker container.
    params: shell_type: The shell type to use for activating the virtual environment (bash or fish).
    """
    if shell_type == "bash":
        # Activating virtual environment and running commit_message.py in Bash
        command = (
            f"docker exec {container_id} bash -c 'source /app/env/bin/activate && "
            f"python /app/scripts/commit_message.py && echo \"Script executed successfully.\"'"
        )
    elif shell_type == "fish":
        # Activating virtual environment and running commit_message.py in Fish
        command = (
            f"docker exec {container_id} fish -c 'source /app/env/bin/activate.fish && "
            f"python /app/scripts/commit_message.py && echo \"Script executed successfully.\"'"
        )
    else:
        logger.error(f"Unsupported shell type: {shell_type}")
        return

    logger.info(f"Activating virtual environment and running commit_message.py in the container {container_id} using {shell_type}.")
    run_command(command, interactive=True)


def main():
    # 1. Check if running in Docker
    check_if_running_in_docker()

    # 2. Add SSH key if not already added
    # add_ssh_key('id_babakbandpey')

    # 3. Find the container ID of the running container
    logger.info(run_command("docker ps -q"))
    logger.info(run_command("docker ps -q --filter ancestor='pipeline-pipeline'"))
    container_id = run_command("docker ps -q --filter ancestor='pipeline-pipeline'")[0].strip()
    logger.info(f"container_id: {container_id}")
    if not container_id:
        logger.error("No running container found with the specified image.")
        exit(1)

    logger.info(f"Running container found: {container_id}")

    # 4. Stage all changes, including new files
    try:
        run_command("git add -A", interactive=True)
        logger.info("All changes, including new files, have been staged.")
    except Exception as e:
        logger.error("Error adding all changes to git staging.")
        logger.error(str(e))
        exit(1)

    # 5. Show the status of the repository
    try:
        status_output, _ = run_command("git status", interactive=True)
        logger.info("Current git status after staging changes:\n" + status_output)
    except Exception as e:
        logger.error("Error retrieving git status.")
        logger.error(str(e))
        exit(1)

    # 6. Generate the git diff of staged changes and save it to diff.txt
    try:
        run_command("git diff --cached > ./commit/diff.txt")
        check_file_exists("./commit/diff.txt")
        if os.path.getsize("./commit/diff.txt") == 0:
            logger.info("No staged changes detected in the repository.")
            exit(1)
        logger.info("Git diff (staged changes) generated and saved to ./commit/diff.txt")
    except Exception as e:
        logger.error("Error generating git diff.")
        logger.error(str(e))
        exit(1)

    # 7. Run the commit_message.py script inside the Docker container
    try:

        logger.info("Executing commit_message.py inside the Docker container to generate commit message.")
        # run_command(f"docker exec {container_id} python /app/scripts/commit_message.py")
        activate_virtualenv_and_run_script(container_id, shell_type="bash")
    except Exception as e:
        logger.error("Error executing commit_message.py inside the Docker container.")
        logger.error(str(e))
        exit(1)

    # 8. Check if commit_message.txt was created
    logger.info("Checking if commit message was generated successfully.")
    check_file_exists("./commit/commit_message.txt")
    logger.info("Commit message generated successfully inside the container.")

    # 9. Commit the changes with the generated commit message
    try:
        if os.path.getsize("./commit/commit_message.txt") < 100:
            logger.error(f"The commit message file is empty or too short.")
            logger.error("Commit message not generated.")
            exit(1)

        logger.info("Committing changes with the generated commit message.")
        run_command("git commit -F ./commit/commit_message.txt")
        logger.info("Changes committed successfully.")
    except Exception as e:
        logger.error("Error committing changes.")
        logger.error(str(e))
        exit(1)

    # 10. Push the changes to the remote repository
    try:
        logger.info("Pushing changes to the remote repository.")
        run_command("git push")
        logger.info("Changes pushed to the remote repository.")
    except Exception as e:
        logger.error("Error pushing changes to the remote repository.")
        logger.error(str(e))
        exit(1)

if __name__ == "__main__":
    main()
