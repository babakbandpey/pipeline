"""
This script scans the codebase and tries to write a README.md file
"""

import os

import datetime
from pipeline import PipelineUtils, FileUtils, logger


def main():
    """Main function to scan the codebase."""

    args = PipelineUtils.get_args()
    args.type = "python"

    if args.path:
        files = FileUtils.get_files_from_path(args.path, ".py")
    else:
        files = FileUtils.get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/README{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)

        chatbot = PipelineUtils.create_chatbot(args)

        logger.info("Analyzing %s...", file)
        logger.debug(chatbot.documents)

        logger.info("Analyzing %s...", file)
        FileUtils.write_to_file(output_file, f"# Analyzing {file}...")

        response = chatbot.invoke(
            "Analyze the code in content for potential issues and security vulnerabilities. " +
            "Be precise about the line number and the issue."
        )

        FileUtils.write_to_file(output_file, response)

        response = chatbot.invoke(
            f"Suggest improvements for the code in '{file}'."
        )

        FileUtils.write_to_file(output_file, response)

        response = chatbot.invoke(
            f"Score the code in '{file}' on a scale of 1 to 10."
        )

        FileUtils.write_to_file(output_file, response)

        chatbot.delete_collection()
        chatbot.clear_chat_history()


if __name__ == "__main__":
    main()
