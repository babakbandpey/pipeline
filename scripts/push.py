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
from datetime import datetime
from pipeline import PipelineUtils, ChatbotUtils

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        ChatbotUtils.logger().exception("Error running command '%s': %s", " ".join(command), e)
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
    ChatbotUtils.logger().info("Staging all changes...")
    run_command(["git", "add", "-A"])

def unstage_changes():
    """Unstage all changes."""
    ChatbotUtils.logger().info("Unstaging all changes...")
    run_command(["git", "reset"])

def generate_diff():
    """Generate diff.txt including all changes."""
    ChatbotUtils.logger().info("Generating diff.txt...")
    try:
        with open("diff.txt", "w", encoding='utf-8') as diff_file:
            diff, _ = run_command(["git", "diff", "--staged"])
            diff_file.write(diff)
    except IOError as e:
        ChatbotUtils.logger().exception("Error generating diff.txt: %s", e)
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
            ChatbotUtils.logger().warning("Branch name cannot be 'main'. Please choose another name.")
            continue

        if branch_exists(new_branch_name):
            ChatbotUtils.logger().warning("Branch name '%s' already exists. Please choose another name.", new_branch_name)
            continue

        ChatbotUtils.logger().info("Creating and checking out new branch: %s", new_branch_name)
        run_command(["git", "checkout", "-b", new_branch_name])
        return new_branch_name

def run_tests():
    """Run pytest and abort if tests fail."""
    ChatbotUtils.logger().info("Running tests...")
    try:
        run_command(["pytest"])
    except subprocess.CalledProcessError:
        ChatbotUtils.logger().exception("Tests failed. Aborting commit.")
        sys.exit(1)
    ChatbotUtils.logger().info("All tests passed.")


def run_checks(chatbot):
    """
    Run checks before committing the changes.
    params: chatbot: The chatbot object to interact with the AI model.
    return: True if all checks pass, False otherwise.
    """

    security_check = chatbot.invoke(
        "Confirm that the changes does not contain any sensitive information."
    )

    if security_check:
        ChatbotUtils.logger().info("Security check: %s", security_check)
        response = input("Is the security check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    vulnerability_check = chatbot.invoke(
        "Confirm that the changes does not introduce any security vulnerabilities."
    )

    if vulnerability_check:
        ChatbotUtils.logger().info("Vulnerability check: %s", vulnerability_check)
        response = input("Is the vulnerability check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    code_quality_check = chatbot.invoke(
        "Confirm that the changes meet the code quality standards."
    )

    if code_quality_check:
        ChatbotUtils.logger().info("Code quality check: %s", code_quality_check)
        response = input("Is the code quality check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    pylint_check = chatbot.invoke(
        "Confirm that the changes pass the pylint check."
    )

    if pylint_check:
        ChatbotUtils.logger().info("Pylint check: %s", pylint_check)
        response = input("Is the pylint check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    improvement_check = chatbot.invoke(
        """
        Write 1 suggestion for code improvement of the changes and format it as a JSON.
        The JSON should contain the following keys
        'path': 'The path of the file',
        'line': 'The line number where the improvement is suggested',
        'snippet': 'The code snippet where the improvement is suggested',
        'suggestion': 'The suggestion for improvement'
        'suggested_change': 'The suggested improved code snippet'
        'function': 'The function name where the improvement is suggested if applicable'
        """
    )

    if improvement_check:
        ChatbotUtils.logger().info(improvement_check)

    response = input("Do you want to implement the improvement? (y/n): ").strip().lower()
    if response == "y":
        return False

    return True

def create_commit_message(chatbot):
    """Create a commit message."""
    ChatbotUtils.logger().info("Running chatbot.py to generate commit message...")
    try:
        while True:
            commit_message = chatbot.invoke(
                """
                Write a detailed commit message based on the provided context.
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
                    ChatbotUtils.logger().warning("Invalid JSON format. Truing again... CTRL+C to abort.")
                    continue
                commit_message = commit_message_json.get('title', 'No Title!')
                commit_message += "\n\nDescription:\n"
                description = commit_message_json.get('description', ['No Description!'])
                for i, sentence in enumerate(description, start=1):
                    commit_message += f"{i}. {sentence.strip()}.\n"
                commit_message += f"\nType: {commit_message_json.get('type', 'No Type!')}"

                ChatbotUtils.logger().info("Generated commit message: %s", commit_message)
                response = input("Is the commit message okay? (y/n): ").strip().lower()
                if response == "y":
                    with open("commit_message.txt", "w", encoding='utf-8') as commit_message_file:
                        commit_message_file.write(commit_message)
                    break

        return True

    except KeyboardInterrupt:
        ChatbotUtils.logger().exception("Aborting commit.")
    except ValueError as e:
        ChatbotUtils.logger().exception("Error generating commit message: %s", e)
    except Exception as e:
        ChatbotUtils.logger().exception("Error: %s", e)

    return False

def cleanup():
    """
    Cleanup temporary files.
    return: True if cleanup is successful, False otherwise.
    """

    try:
        os.remove("diff.txt")
    except OSError as e:
        ChatbotUtils.logger().error("Error removing diff.txt: %s", e)
        return False

    try:
        os.remove("commit_message.txt")
    except OSError as e:
        ChatbotUtils.logger().error("Error removing commit_message.txt: %s", e)
        return False

    return True


def main():
    """The main function."""

    # Step 0: Check if there are any changes to commit
    if not has_changes_to_commit():
        ChatbotUtils.logger().info("No changes to commit.")
        # push changes to remote
        run_command(["git", "push"])
        sys.exit(0)

    # Step 1: Get the current branch name
    branch_name = get_current_branch_name()
    ChatbotUtils.logger().info("Current branch: %s", branch_name)

    # Step 2: Handle being on the main branch
    if branch_name == "main":
        ChatbotUtils.logger().info("Currently on the main branch. Creating a new branch.")
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
    chatbot = PipelineUtils.create_chatbot(args)

    # Step 7: Run checks before committing the changes
    if not run_checks(chatbot) or not create_commit_message(chatbot):
        ChatbotUtils.logger().info("Aborting commit.")
        unstage_changes()
        cleanup()
        sys.exit(0)

    response = input("Do you want to continue with the commit? (y/n): ").strip().lower()
    if response == "n":
        ChatbotUtils.logger().info("Aborting commit.")
        sys.exit(0)

    # Step 8: Perform git commit
    ChatbotUtils.logger().info("Committing changes...")
    run_command(["git", "commit", "-aF", "commit_message.txt"])

    # Step 9: Cleanup
    ChatbotUtils.logger().info("Cleaning up...")
    cleanup()

    # Step 10: Set upstream branch and push changes
    ChatbotUtils.logger().info("Setting upstream branch to %s and pushing changes...", branch_name)
    run_command(["git", "push", "--set-upstream", "origin", branch_name])


if __name__ == "__main__":
    main()
