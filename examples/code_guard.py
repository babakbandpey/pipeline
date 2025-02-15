"""
This script scans the codebase for any potential issues
and reports them back to the user.
Except for the env directory, it will check all files in the
For now it only scans the python files.
"""

import os

import datetime
from pipeline import PipelineUtils, FileUtils, logger


def main():
    """Main function to scan the codebase."""

    args = PipelineUtils.get_args()
    args.type = "py"

    if args.path:
        files = FileUtils.get_files(args.path, ".py")
    else:
        files = FileUtils.get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/code_guard_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)

        chatbot = PipelineUtils.create_chatbot(args)

        logger.info("Analyzing %s...", file)
        logger.debug(chatbot.documents)

        logger.info("Analyzing %s...", file)
        FileUtils.write_to_file(output_file, f"# Analyzing {file}...", mode="a")

        response = chatbot.invoke(
            "Analyze the code in content for potential issues and security vulnerabilities. " +
            "Be precise about the line number and the issue."
        )

        FileUtils.write_to_file(output_file, response, mode="a")

        response = chatbot.invoke(
            f"Suggest improvements for the code in '{file}'."
        )

        FileUtils.write_to_file(output_file, response, mode="a")

        response = chatbot.invoke(
            f"Score the code in '{file}' on a scale of 1 to 10."
        )

        FileUtils.write_to_file(output_file, response, mode="a")

        chatbot.delete_collection()
        chatbot.clear_chat_history()


if __name__ == "__main__":
    main()
