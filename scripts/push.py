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
import json
from datetime import datetime
from pipeline import Utils

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
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
    print("Staging all changes...")
    run_command(["git", "add", "-A"])

def unstage_changes():
    """Unstage all changes."""
    print("Unstaging all changes...")
    run_command(["git", "reset"])

def generate_diff():
    """Generate diff.txt including all changes."""
    print("Generating diff.txt...")
    try:
        with open("diff.txt", "w", encoding='utf-8') as diff_file:
            diff, _ = run_command(["git", "diff", "--staged"])
            diff_file.write(diff)
    except IOError as e:
        print(f"Error generating diff.txt: {e}")
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
            print("Branch name cannot be 'main'. Please choose another name.")
            continue

        if branch_exists(new_branch_name):
            print(f"Branch name '{new_branch_name}' already exists. Please choose another name.")
            continue

        print(f"Creating and checking out new branch: {new_branch_name}")
        run_command(["git", "checkout", "-b", new_branch_name])
        return new_branch_name

def run_tests():
    """Run pytest and abort if tests fail."""
    print("Running tests...")
    try:
        run_command(["pytest"])
    except subprocess.CalledProcessError:
        print("Tests failed. Aborting commit.")
        sys.exit(1)
    print("All tests passed.")


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
        print(f"Security check: {security_check}")
        response = input("Is the security check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    vulnerability_check = chatbot.invoke(
        "Confirm that the changes does not introduce any security vulnerabilities."
    )

    if vulnerability_check:
        print(f"Vulnerability check: {vulnerability_check}")
        response = input("Is the vulnerability check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    code_quality_check = chatbot.invoke(
        "Confirm that the changes meet the code quality standards."
    )

    if code_quality_check:
        print(f"Code quality check: {code_quality_check}")
        response = input("Is the code quality check okay? (y/n): ").strip().lower()
        if response == "n":
            return False

    pylint_check = chatbot.invoke(
        "Confirm that the changes pass the pylint check."
    )

    if pylint_check:
        print(f"Pylint check: {pylint_check}")
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
        print(improvement_check)

    response = input("Do you want to implement the improvement? (y/n): ").strip().lower()
    if response == "y":
        return False

    return True

def create_commit_message(chatbot):
    """Create a commit message."""
    print("Running chatbot.py to generate commit message...")
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
                'description': 'The description of the commit message',
                'type': 'The type of the commit message (e.g. feature, bugfix, etc.)',
                """
            )

            if commit_message:
                print(f"Generated commit message: {commit_message}")
                response = input("Is the commit message okay? (y/n): ").strip().lower()
                if response == "y":

                    commit_message = commit_message.replace("```json", "").replace("```", "")
                    commit_message_json = json.loads(commit_message)
                    commit_message = commit_message_json['title']
                    commit_message += commit_message_json['description']
                    commit_message += f"Type: {commit_message_json['type']}"

                    with open("commit_message.txt", "w", encoding='utf-8') as commit_message_file:
                        commit_message_file.write(commit_message)

                    break
        return True

    except KeyboardInterrupt:
        print("Aborting commit.")
    except ValueError as e:
        print(f"Error generating commit message: {e}")
    except Exception as e:
        print(f"Error: {e}")

    return False

def main():
    """The main function."""

    # Step 0: Check if there are any changes to commit
    if not has_changes_to_commit():
        print("No changes to commit.")
        # push changes to remote
        run_command(["git", "push"])
        return

    # Step 1: Get the current branch name
    branch_name = get_current_branch_name()
    print(f"Current branch: {branch_name}")

    # Step 2: Handle being on the main branch
    if branch_name == "main":
        print("Currently on the main branch. Creating a new branch.")
        branch_name = create_and_checkout_new_branch()

    # Step 3: Stage all changes
    stage_changes()

    # Step 4: Generate diff.txt
    generate_diff()

    # Step 5: Run tests and abort if they fail
    run_tests()

    # Step 6: Run chatbot to generate commit message
    args = Utils.get_args()
    args.type = "text"
    args.path = "diff.txt"
    chatbot = Utils.create_chatbot(args)

    if not run_checks(chatbot):
        print("Aborting commit.")
        unstage_changes()
        sys.exit(1)


    if not create_commit_message(chatbot):
        print("Aborting commit.")
        unstage_changes()
        sys.exit(1)

    response = input("Do you want to continue with the commit? (y/n): ").strip().lower()
    if response == "n":
        print("Aborting commit.")
        sys.exit(1)

    # Step 7: Perform git commit
    print("Committing changes...")
    run_command(["git", "commit", "-aF", "commit_message.txt"])

    # Step 8: Set upstream branch and push changes
    print(f"Setting upstream branch to {branch_name} and pushing changes...")
    run_command(["git", "push", "--set-upstream", "origin", branch_name])

    # Step 9: Cleanup
    print("Cleaning up...")
    try:
        os.remove("diff.txt")
    except OSError as e:
        print(f"Error removing diff.txt: {e}")

    try:
        os.remove("commit_message.txt")
    except OSError as e:
        print(f"Error removing commit_message.txt: {e}")

if __name__ == "__main__":
    main()
