"""
This script scans the codebase for any potential issues
and reports them back to the user.
Except for the env directory, it will check all files in the
For now it only scans the python files.
"""

import os
import logging
import datetime
from utils import create_chatbot, get_args, write_to_file, get_files

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """Main function to scan the codebase."""

    args = get_args()
    args.class_type = "PythonRAG"


    if args.path:
        if not os.path.exists(args.path):
            logging.error("Error: The path '%s' does not exist.", args.path)
            return

        if os.path.isfile(args.path):
            files = [args.path]
        else:
            files = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith(".py")]

    else:
        files = get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/code_chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)

        chatbot = create_chatbot(args)

        logging.info("Analyzing %s...", file)
        write_to_file(output_file, f"# Analyzing {file}...")

        response = chatbot.invoke(
            "Analyze the code in the content and write a description of what the code does. "
        )

        write_to_file(output_file, response)

        response = chatbot.invoke(
            "Write a description of the code in the content, " +
            "which could be used in creating a detailed flow chart ."
        )

        write_to_file(output_file, response)

        chatbot.delte_vector_store()
        chatbot.clear_chat_history()


if __name__ == "__main__":
    main()
