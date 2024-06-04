"""
This script is a simple AI Agent which will
create commit messages for you and commit the changes.
"""

import subprocess
import sys
import os
from datetime import datetime
from utils import create_chatbot, get_args

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
    args = get_args()
    args.class_type = "TextRAG"
    args.path = "diff.txt"
    chatbot = create_chatbot(args)

    print("Running chatbot.py to generate commit message...")
    try:
        commit_message = chatbot.invoke(
            "Find the git difference in the content and write a commit " +
            "message based on the provided context." +
            " Do not include any extra information in the" +
            " commit message such as code or anything else." +
            " Format the commit message as a single line."
        )
    except Exception as e:
        print(f"Error generating commit message: {e}")
        sys.exit(1)

    # replace the new line characters with a space
    commit_message = commit_message.replace("\n", " ").strip()

    # Step 7: Perform git commit
    print("Committing changes...")
    print(f"Commit message: {commit_message}")
    run_command(["git", "commit", "-am", commit_message])

    # Step 8: Set upstream branch and push changes
    print(f"Setting upstream branch to {branch_name} and pushing changes...")
    run_command(["git", "push", "--set-upstream", "origin", branch_name])

    # Step 9: Cleanup
    print("Cleaning up...")
    try:
        os.remove("diff.txt")
    except OSError as e:
        print(f"Error removing diff.txt: {e}")

if __name__ == "__main__":
    main()
