"""
This script scans the codebase for any potential issues
and reports them back to the user.
Except for the env directory, it will check all files in the
For now it only scans the python files.
"""

import os
import logging
import datetime
from pipeline import Utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """Main function to scan the codebase."""

    args = Utils.get_args()
    args.type = "python"

    if args.path:
        files = Utils.get_files_from_path(args.path, ".py")
    else:
        files = Utils.get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/code_chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)

        chatbot = Utils.create_chatbot(args)

        logging.info("Analyzing %s...", file)
        Utils.write_to_file(output_file, f"# Analyzing {file}...")

        response = chatbot.invoke(
            "Analyze the code in the content and write a description of what the code does. "
        )

        Utils.write_to_file(output_file, response)

        response = chatbot.invoke(
            "Write a description of the code in the content, " +
            "which could be used in creating a detailed flow chart ."
        )

        Utils.write_to_file(output_file, response)

        chatbot.delte_vector_store()
        chatbot.clear_chat_history()


if __name__ == "__main__":
    main()
