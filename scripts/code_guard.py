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
        files = Utils.get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/code_guard_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)

        chatbot = Utils.create_chatbot(args)

        logging.info("Analyzing %s...", file)
        Utils.write_to_file(output_file, f"# Analyzing {file}...")

        response = chatbot.invoke(
            f"Analyze the code in '{file}' for potential issues and security vulnerabilities. " +
            "Be precise about the line number and the issue."
        )

        Utils.write_to_file(output_file, response)

        response = chatbot.invoke(
            f"Suggest improvements for the code in '{file}'."
        )

        Utils.write_to_file(output_file, response)

        response = chatbot.invoke(
            f"Score the code in '{file}' on a scale of 1 to 10."
        )

        Utils.write_to_file(output_file, response)

        chatbot.delte_vector_store()
        chatbot.clear_chat_history()


if __name__ == "__main__":
    main()
