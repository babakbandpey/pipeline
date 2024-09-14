"""
This script is a simple AI Agent which will
help you to commit your changes to the repository.

The script performs the following steps:
1. Checks if there are any changes to commit.
2. Gets the current branch name and handles being on the main branch.
3. Stages all changes.
4. Generates a diff.txt file including all changes.
5. Runs tests and aborts if they fail.
6. Runs a chatbot to perform checks before committing the changes,
    including security check, vulnerability check, code quality check, and pylint check.
7. Asks for suggestions for code improvement and allows the user to implement them.
8. Creates a commit message using the chatbot.
9. Asks for confirmation to continue with the commit.
10. Performs the git commit.
11. Sets the upstream branch and pushes the changes.
12. Cleans up temporary files.

The script relies on the 'pipeline' module, which provides utility functions for
    running shell commands and creating a chatbot.

Note: This script assumes that the necessary dependencies are installed and
    the repository is properly configured with Git.
"""

import subprocess
import sys
import os
import secrets
from datetime import datetime
from pipeline import PipelineUtils, ChatbotUtils, logger

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        return result.stdout.strip(), result.returncode
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


def cleanup():
    """
    Cleanup temporary files.
    return: True if cleanup is successful, False otherwise.
    """

    try:
        os.remove("diff.txt")
    except OSError as e:
        logger.error("Error removing diff.txt: %s", e)
        return False

    try:
        os.remove("commit_message.txt")
    except OSError as e:
        logger.error("Error removing commit_message.txt: %s", e)
        return False

    return True


def main():
    """The main function."""

    # Step 0: Check if there are any changes to commit
    if not has_changes_to_commit():
        logger.info("No changes to commit.")
        # push changes to remote
        run_command(["git", "push"])
        sys.exit(0)

    # Step 1: Get the current branch name
    branch_name = get_current_branch_name()
    logger.info("Current branch: %s", branch_name)

    # Step 2: Handle being on the main branch
    if branch_name == "main":
        logger.info("Currently on the main branch. Creating a new branch.")
        branch_name = create_and_checkout_new_branch()

    # Step 3: Stage all changes
    stage_changes()

    # Step 4: Generate diff.txt
    generate_diff()

    # Step 5: Run tests and abort if they fail
    run_tests()

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
        cleanup()
        sys.exit(0)

    response = input("Do you want to continue with the commit? (y/n): ").strip().lower()
    if response == "n":
        logger.info("Aborting commit.")
        sys.exit(0)

    # Step 8: Perform git commit
    logger.info("Committing changes...")
    run_command(["git", "commit", "-aF", "commit_message.txt"])

    # Step 9: Cleanup
    logger.info("Cleaning up...")
    cleanup()

    # Step 10: Set upstream branch and push changes
    logger.info("Setting upstream branch to %s and pushing changes...", branch_name)
    run_command(["git", "push", "--set-upstream", "origin", branch_name])

    chatbot.delete_collection()
    chatbot.clear_chat_history()

if __name__ == "__main__":
    main()
