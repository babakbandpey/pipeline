"""
This script scans the codebase for any potential issues
and reports them back to the user.
Except for the env directory, it will check all files in the
For now it only scans the python files.
"""

import os
import logging
import datetime
import secrets
from pipeline import PipelineUtils, FileUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """Main function to scan the codebase."""

    args = PipelineUtils.get_args()
    args.type = "py"

    if args.path:
        files = FileUtils.get_files(args.path, ".py")
    else:
        files = FileUtils.get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/code_chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)
        args.collection_name = secrets.token_hex(16)
        chatbot = PipelineUtils.create_chatbot(args)

        logging.info("Analyzing %s...", file)
        FileUtils.write_to_file(output_file, f"# Analyzing {file}...", mode="a")

        response = chatbot.invoke(
            "Analyze the code in the content and write a description of what the code does. "
        )

        FileUtils.write_to_file(output_file, response, mode="a")

        response = chatbot.invoke(
            "Write a description of the code in the content, " +
            "which could be used in creating a detailed flow chart ."
        )

        FileUtils.write_to_file(output_file, response, mode="a")

        chatbot.delete_collection()
        chatbot.clear_chat_history()


if __name__ == "__main__":
    main()
