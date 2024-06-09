"""
This script scans the codebase for any potential issues
and reports them back to the user.
Except for the env directory, it will check all files in the
For now it only scans the python files.
"""

import os

import datetime
from pipeline import PipelineUtils, FileUtils, ChatbotUtils


def main():
    """Main function to scan the codebase."""

    args = PipelineUtils.get_args()
    args.type = "python"

    if args.path:
        files = FileUtils.get_files_from_path(args.path, ".py")
    else:
        files = FileUtils.get_files()

    # create an output file with timestamp .md file and write the response to it
    output_file = f"./history/code_guard_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    for file in files:

        # get absolute path of the file
        args.path = os.path.abspath(file)

        chatbot = PipelineUtils.create_chatbot(args)

        ChatbotUtils.logger().info("Analyzing %s...", file)
        ChatbotUtils.logger().debug(chatbot.documents)

        ChatbotUtils.logger().info("Analyzing %s...", file)
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
