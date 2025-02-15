import subprocess
import os
import sys
import secrets
from datetime import datetime
from pipeline import PipelineUtils, ChatbotUtils, logger
import platform

# Configure the logger

# Create file handler to save logs to push.log
file_handler = logger.FileHandler('./logs/push.log')
file_handler.setLevel(logger.INFO)

# Create console handler to print logs to stdout
console_handler = logger.StreamHandler()
console_handler.setLevel(logger.INFO)


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
        logger.exception("Error running command '%s': %s", " ".join(command), e)
        sys.exit(e.returncode)

def has_changes_to_commit():
    """Check if there are any changes to commit."""
    status, _ = run_command(["git", "status", "--porcelain"])
    return bool(status)

def get_current_branch_name():
    """Get the current git branch name."""
    branch_name, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return branch_name

def stage_changes():
    """Stage all changes including untracked files."""
    logger.info("Staging all changes...")
    run_command(["git", "add", "-A"])

def unstage_changes():
    """Unstage all changes."""
    logger.info("Unstaging all changes...")
    run_command(["git", "reset"])

def generate_diff():
    """Generate diff.txt including all changes."""
    logger.info("Generating diff.txt...")
    try:
        with open("diff.txt", "w", encoding='utf-8') as diff_file:
            diff, _ = run_command(["git", "diff", "--staged"])
            diff_file.write(diff)
    except IOError as e:
        logger.error("Error generating diff.txt: %s", e)
        sys.exit(1)

def branch_exists(branch_name):
    """Check if a branch already exists."""
    existing_branches, _ = run_command(["git", "branch", "--list"])
    return branch_name in existing_branches.split()

def create_and_checkout_new_branch():
    """Create a new branch and switch to it."""
    while True:
        new_branch_name = input(
            "Enter the new branch name (or leave empty to auto-generate): "
        ).strip()

        if not new_branch_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_branch_name = f"branch_{timestamp}"

        if new_branch_name == "main":
            logger.warning("Branch name cannot be 'main'. Please choose another name.")
            continue

        if branch_exists(new_branch_name):
            logger.warning("Branch name '%s' already exists. Please choose another name.", new_branch_name)
            continue

        logger.info("Creating and checking out new branch: %s", new_branch_name)
        run_command(["git", "checkout", "-b", new_branch_name])
        return new_branch_name


def run_tests():
    """Run pytest and abort if tests fail."""
    logger.info("Running tests...")
    try:
        run_command(["pytest"])
    except subprocess.CalledProcessError as e:
        logger.exception("Tests failed. Aborting commit. %s", e)
        sys.exit(1)
    logger.info("All tests passed.")


def run_pylint(file):
    """
    Run pylint on a given file and return the result.
    params: file: The file to run pylint on.
    return: The output of pylint.
    """
    try:
        result = subprocess.run(['pylint', file], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.output



def run_checks(args):
    """
    Run checks before committing the changes.
    params: args: The arguments to pass to the chat
    return: True if all checks pass, False otherwise.
    """
    try:
        modified_files, moved_files, added_files, _ = get_changed_files()
        if not (modified_files or moved_files or added_files):
            logger.info("No changed, added, or moved files found.")
            return False

        all_files = list(modified_files) + list(moved_files.values()) + list(added_files)

        for file in all_files:

            accepted_file_types = [".py", ".txt", ".json", ".md"]
            if not any(file.endswith(file_type) for file_type in accepted_file_types):
                logger.warning("Unsupported file type: %s. Skipping checks...", file)
                continue

            # create chatbot based on file type
            file_type = os.path.splitext(file)[1][1:]
            args.type = file_type
            args.path = file
            args.collection_name = secrets.token_hex(16)
            chatbot = PipelineUtils.create_chatbot(args)

            security_check = chatbot.invoke(
                f"Confirm that the changes do not contain any sensitive information in the file: {file}"
            )

            if security_check:
                logger.info("Security check for %s: %s", file, security_check)
                response = input(f"Is the security check for {file} okay? (y/n): ").strip().lower()
                if response == "n":
                    return False

            vulnerability_check = chatbot.invoke(
                f"Confirm that the changes do not introduce any security vulnerabilities in the file: {file}"
            )

            if vulnerability_check:
                logger.info("Vulnerability check for %s: %s", file, vulnerability_check)
                response = input(f"Is the vulnerability check for {file} okay? (y/n): ").strip().lower()
                if response == "n":
                    return False

            code_quality_check = chatbot.invoke(
                f"Confirm that file meet the code quality standards in the file: {file}"
            )

            if code_quality_check:
                logger.info("Code quality check for %s: %s", file, code_quality_check)
                response = input(f"Is the code quality check for {file} okay? (y/n): ").strip().lower()
                if response == "n":
                    return False

            pylint_check = run_pylint(file)
            if pylint_check:
                logger.info("Pylint check for %s: %s", file, pylint_check)
                response = input(f"Is the pylint check for {file} okay? (y/n): ").strip().lower()
                if response == "n":
                    return False

            improvement_check = chatbot.invoke(
                f"""
                Write 1 suggestion for code improvement of the changes in the file: {file} and format it as a JSON.
                The JSON should contain the following keys:
                'path': 'The path of the file',
                'line': 'The line number where the improvement is suggested',
                'snippet': 'The code snippet where the improvement is suggested',
                'suggestion': 'The suggestion for improvement',
                'suggested_change': 'The suggested improved code snippet',
                'function': 'The function name where the improvement is suggested if applicable'
                """
            )

            if improvement_check:
                logger.info("Improvement suggestion for %s: %s", file, improvement_check)

            response = input(f"Do you want to implement the improvement for {file}? (y/n): ").strip().lower()
            if response == "y":
                return False


            chatbot.delete_collection()
            chatbot.clear_chat_history()

        return True

    except subprocess.CalledProcessError as e:
        logger.error("Error running git status: %s", e)
        return False
    except Exception as e:
        logger.error("An error occurred: %s", e)
        return False

def get_changed_files() -> tuple:
    """
    Get the list of changed, added, or moved files.
    return: A tuple containing the modified files, moved files, and added files.
    """
    try:
        result = subprocess.run(['git', 'status', '-M', '--porcelain'], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Error running git status: %s", e)
        raise e

    modified_files = set()
    added_files = set()
    moved_files = {}
    deleted_files = set()

    for line in result.stdout.splitlines():
        status, file_path = line[:2], line[3:]
        if status == 'M ':
            modified_files.add(file_path)
        elif status == 'A ':
            added_files.add(file_path)
        elif status.startswith('R'):
            old_file, new_file = file_path.split(' -> ')
            moved_files[old_file] = new_file
        elif status == 'D ':
            deleted_files.add(file_path)

    return modified_files, moved_files, added_files, deleted_files

def generate_commit_message(chatbot, context):
    """
    Generate a commit message using the chatbot based on the provided context.
    params: chatbot: The chatbot object to interact with the AI model.
    params: context: The context for generating the commit message.
    """
    while True:
        commit_message = chatbot.invoke(
            f"""
            Write a detailed commit message based on the provided context.
            {context}
            Write the title of the commit message in the first line.
            Do not include any extra information in the
            commit message such as code.
            Format the commit message as JSON.
            The JSON should contain the following keys:
            'title': 'The title of the commit message',
            'description': ['The description of the commit message as a list of sentences.'],
            'type': 'The type of the commit message (e.g. feature, bugfix, etc.)',
            """
        )

        if commit_message:
            commit_message_json = ChatbotUtils.parse_json(commit_message)
            if commit_message_json is None:
                logger.warning("Invalid JSON format. Trying again... CTRL+C to abort.")
                continue

            title = commit_message_json.get('title', 'No Title!')
            description = commit_message_json.get('description', ['No Description!'])
            commit_type = commit_message_json.get('type', 'No Type!')

            commit_message_formatted = f"{title}\n\nDescription:\n"
            for i, sentence in enumerate(description, start=1):
                commit_message_formatted += f"{i}. {sentence.strip()}.\n"
            commit_message_formatted += f"\nType: {commit_type}\n"

            return commit_message_formatted

def create_commit_message(chatbot):
    """
    Create a commit message.
    params: chatbot: The chatbot object to interact with the AI model.
    """
    logger.info("Running chatbot.py to generate commit message...")

    try:
        modified_files, moved_files, added_files, deleted_files = get_changed_files()
        if not (modified_files or moved_files or added_files):
            logger.info("No changed, added, or moved files found.")
            return False

        consolidated_commit_message = ""

        for file in modified_files:
            context = f"The file that has been changed is: {file}"
            commit_message_formatted = generate_commit_message(chatbot, context)
            consolidated_commit_message += commit_message_formatted + "\n"

        for old_file, new_file in moved_files.items():
            context = f"The file that has been moved is from: {old_file} to {new_file}"
            commit_message_formatted = generate_commit_message(chatbot, context)
            consolidated_commit_message += commit_message_formatted + "\n"

        for file in added_files:
            context = f"The file that has been added is: {file}"
            commit_message_formatted = generate_commit_message(chatbot, context)
            consolidated_commit_message += commit_message_formatted + "\n"

        for file in deleted_files:
            context = f"The file that has been deleted is: {file}"
            commit_message_formatted = generate_commit_message(chatbot, context)
            consolidated_commit_message += commit_message_formatted + "\n"

        logger.info("Generated consolidated commit message: %s", consolidated_commit_message)
        response = input("Is the consolidated commit message okay? (y/n): ").strip().lower()
        if response == "y":
            with open("commit_message.txt", "w", encoding='utf-8') as commit_message_file:
                commit_message_file.write(consolidated_commit_message)
            return True

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        return False

    return False

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
        logger.error("SSH key not found at %s. Please ensure it exists.", ssh_key_path)
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

        logger.info("SSH key %s added to the ssh-agent.", ssh_key_path)

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
        logger.info("Current git status after staging changes:\n %s", status_output)
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

    # Step 6: Create a chatbot to perform checks before committing the changes
    args = PipelineUtils.get_args()
    args.type = "txt"
    args.path = "diff.txt"
    args.collection_name = secrets.token_hex(16)
    chatbot = PipelineUtils.create_chatbot(args)

    # Step 7: Run checks before committing the changes
    if not run_checks(args) or not create_commit_message(chatbot):
        logger.info("Aborting commit.")
        unstage_changes()
        sys.exit(0)
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
            logger.error("The commit message file is empty or too short.")
            logger.error("Commit message not generated.")
            exit(1)

        logger.info("Committing changes with the generated commit message.")
        run_command("git commit -F ./commit/commit_message.txt")
        logger.info("Changes committed successfully.")
    except Exception as e:
        logger.error("Error committing changes.")
        logger.error(str(e))
        exit(1)

    chatbot.delete_collection()
    chatbot.clear_chat_history()
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
