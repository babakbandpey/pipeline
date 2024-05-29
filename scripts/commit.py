"""
This script is a simple AI Agent which will
create commit messages for you and commit the changes.
"""

import subprocess
import sys
import os
from utils import create_chatbot, get_args

def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
        sys.exit(result.returncode)
    return result.stdout.strip()


def has_changes_to_commit():
    """Check if there are any changes to commit."""
    status = run_command("git status --porcelain")
    return bool(status)


def get_current_branch_name():
    """Get the current git branch name."""
    return run_command("git rev-parse --abbrev-ref HEAD")


def stage_changes():
    """Stage all changes including untracked files."""
    print("Staging all changes...")
    run_command("git add -A")


def generate_diff():
    """Generate diff.txt including all changes."""
    print("Generating diff.txt...")
    run_command("git diff --staged > diff.txt")


def main():
    """The main function."""

    # Step 0: Check if there are any changes to commit
    if not has_changes_to_commit():
        print("No changes to commit.")
        return

    # Step 1: Get the current branch name
    branch_name = get_current_branch_name()
    print(f"Current branch: {branch_name}")

    # Step 2: Stage all changes
    stage_changes()

    # Step 3: Generate diff.txt
    generate_diff()

    # Step 4: Run chatbot to generate commit message
    args = get_args()
    args.class_type = "TextRAG"
    args.path = "diff.txt"
    chatbot = create_chatbot(args)

    print("Running chatbot.py to generate commit message...")
    commit_message = chatbot.invoke(
        "Find the git difference in the conten and write a commit " +
        "message based on the provided context."
    )

    # Step 5: Perform git commit
    print("Committing changes...")
    run_command(f'git commit -am "{commit_message}"')

    # Step 6: Set upstream branch and push changes
    print(f"Setting upstream branch to {branch_name} and pushing changes...")
    run_command(f"git push --set-upstream origin {branch_name}")

    # Step 7: Cleanup
    print("Cleaning up...")
    # delete diff.txt by python
    os.remove("diff.txt")

if __name__ == "__main__":
    main()
