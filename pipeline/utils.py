"""
Shared utility functions.
"""

import datetime
import os
import sys
import re
import json
import argparse
import logging
from .config import OPENAI_API_KEY
from .chatbot import Chatbot
from .text_rag import TextRAG
from .python_rag import PythonRAG
from .web_rag import WebRAG
from .pdf_rag import PdfRAG

class PipelineUtils():
    """ Utility class for the pipeline. """

    @staticmethod
    def get_args():
        """
        Get the arguments.
        :return: The arguments.
        """

        parser = argparse.ArgumentParser(
            description="Run chatbot with different configurations."
        )

        parser.add_argument(
            "--model",
            type=str,
            required=False,
            help="Model to use.",
            default="gpt-4o"
        )

        parser.add_argument(
            "--type",
            type=str,
            required=False,
            choices=[
            "chat",
            "text",
            "python",
            "web",
            "pdf",
            ],
            help="Class type to use.",
            default="chat"
        )

        parser.add_argument(
            "--path",
            type=str,
            required=False,
            help="Local path to a file or directory.",
            default=None
        )

        parser.add_argument(
            "--url",
            type=str,
            required=False,
            help="URL to a website.",
            default=None
        )

        parser.add_argument("--git_url",
			type=str,
			required=False,
			help="The url to a git repo to be used with the type PythonRAG",
			default=None)
        parser.add_argument("--openai_api_key",
			type=str,
			required=False,
			default=OPENAI_API_KEY,
			help="OpenAI API key.")
        parser.add_argument("--example",
			action="store_true" ,
			required=False,
			help="Showing some examples of how to run the script",
			default=None)
        parser.add_argument("--prompt",
			type=str ,
			required=False,
			help="The prompt",
			default="Say something useful about the content")
        return parser.parse_args()


    @staticmethod
    def handle_command(prompt: str, chatbot: object):
        """
        Handle the command.
        :param prompt: The prompt.
        :param chatbot: The pipeline.Chatbot.
        """

        def save_chat_history():
            """
            Save the chat history.
            :param pipeline: The pipeline.
            """

            if not os.path.exists("history"):
                os.makedirs("history")
            filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            path = os.path.join("history", filename)
            with open(path, "w", encoding='utf-8') as file:
                for index, message in enumerate(chatbot.chat_history.messages):
                    file.write(f"{index + 1}. {message}\n")
            print(f"Chat history saved to {filename}")


        def default_action():
            print("\n\n++Chatbot: ", chatbot.invoke(prompt))


        def exit_chat():
            print("\n\nGoodbye!\n\n")
            sys.exit(0)


        def show_history():
            """
            Show the chat history.
            :return: True if the chat history is shown, False otherwise.
            """
            if not chatbot.chat_history.messages:
                print("No chat history.")
                return False

            for index, message in enumerate(chatbot.chat_history.messages):
                print(f"{index + 1}. {message}")

            return True


        def delete_message():
            """
            Delete a message from the chat history.
            """
            if show_history():
                number = int(input("""
                            Enter the number of the message to delete.
                            Positive number deletes from the beginning.
                            Negative number deletes from the end: """))

                if number:
                    if chatbot.modify_chat_history(number - 1):
                        print("Message deleted.")
                    else:
                        print("Invalid number provided.")
                else:
                    print("Invalid number provided.")


        def print_commands_help():
            """
            Print the commands help.
            """

            print("\n\n++Chatbot: ", """
                Commands:
                /exit (to exit the chatbot),
                /reset (to reset the chat history),
                /history (to see the chat history),
                /delete <index> (e.g., /delete 3 or /delete -4)
                        Number of messages which are to be deleted.
                        Positive index deletes from the start,
                        negative index deletes from the end.
                /summarize (to summarize the chat history),
                /save (to save the chat history),
                /help
                """
            )

        commands = {
            "/exit": exit_chat,
            "/reset": lambda: (chatbot.clear_chat_history(), show_history()),
            "/history": lambda: (show_history(), None)[1],
            "/delete": lambda: (delete_message(), "/history")[1],
            "/summarize": lambda: (chatbot.summarize_messages(), "/history")[1],
            "/save": save_chat_history,
            "/help": print_commands_help
        }

        # Retrieve the function from the dictionary and call it, if not found, call default_action
        action = commands.get(prompt, default_action)
        return action()


    @staticmethod
    def create_chatbot(args):
        """
        Create the chatbot.
        :param args: The arguments.
        :return: The chatbot.
        """

        if args.example:
            print("""
            Examples:
            python .\\scripts\\run.py --type=chat or just python .\\scripts\\run.py
            python .\\scripts\\run.py --type=web --url=https://greydynamics.com/organisation-gladio/
            python .\\scripts\\run.py --type=text --path=c:\\Users\\Me\\Documents\\policies
            python .\\scripts\\run.py --type=pdf --path=c:\\Users\\Me\\Documents\\policies
            python .\\scripts\\run.py --type=python --path=c:\\Users\\Me\\Documents\\project
            """)
            sys.exit(0)

        if args.model == "llaama3":
            base_url = "http://localhost:11434"
            openai_api_key = None
        elif args.model == "phi3":
            base_url = "http://localhost:11434"
            openai_api_key = None
        elif "gpt" in args.model:
            base_url = "https://api.openai.com/v1/"
            openai_api_key = args.openai_api_key
        else:
            base_url = "http://localhost:1234/v1"
            openai_api_key = None

        if hasattr(args, 'collection_name') and args.collection_name is not None:
            collection_name = args.collection_name
        else:
            collection_name = None

        if hasattr(args, 'git_url') and args.git_url is not None:
            git_url = args.git_url
        else:
            git_url = None

        if hasattr(args, 'path') and args.path is not None:
            path = args.path
        else:
            path = None

        if hasattr(args, 'url') and args.url is not None:
            url = args.url
        else:
            url = None

        kwargs = {
            "base_url": base_url,
            "model": args.model,
            "openai_api_key": openai_api_key,
            "collection_name": collection_name,
            "git_url": git_url,
            "path": path,
            "url": url
        }

        if args.type == "chat":
            return Chatbot(**kwargs)

        if args.type == "text":
            return TextRAG(**kwargs)

        if args.type == "python":
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            exclude_patterns = [
                "env/**/*",
                "venv/**/*",
                ".git/**/*",
                ".idea/**/*",
                ".vscode/**/*",
                "**/__pycache__/**/*",
                "**/.pytest_cache/**/*"
            ]
            exclude_paths = [os.path.join(base_path, pattern) for pattern in exclude_patterns]

            kwargs["exclude"] = exclude_paths

            return PythonRAG(**kwargs)

        if args.type == "web":
            return WebRAG(**kwargs)

        if args.type == "pdf":
            return PdfRAG(**kwargs)

        return None

    @staticmethod
    def get_files():
        """Get all python files in the codebase."""
        files = []
        for root, _, filenames in os.walk("."):
            for filename in filenames:
                if filename.endswith(".py") and "env" not in root and '.git' not in root:
                    files.append(os.path.join(root, filename))
        return files


    @staticmethod
    def write_to_file(output_file, response):
        """Write the response to a file."""
        with open(output_file, "a", encoding='utf-8') as file:
            file.write(response)
            file.write("\n\n")

    @staticmethod
    def get_files_from_path(path, file_extension=".py"):
        """Get a list of Python files from the given path."""
        if not os.path.exists(path):
            logging.error("Error: The path '%s' does not exist.", path)
            return []

        if os.path.isfile(path):
            return [path]
        else:
            return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(file_extension)]


    @staticmethod
    def parse_json(response):
        """
        Parse the JSON response and return the JSON object.
        :param response: The response.
        :return: The JSON object.
        """
        response = re.sub(r'```json|```', '', response)
        response_json = json.loads(response)
        return response_json


    @staticmethod
    def parse_json_response(response):
        """
        Parse the JSON response and return the JSON object.
        :param response: The response.
        :return: The JSON object.
        """
        try:
            response_json = PipelineUtils.parse_json(response)

            # controlling if the response_json is a json object
            if isinstance(response_json, dict):
                return response_json
            else:
                return None
        except json.JSONDecodeError:
            logging.error("Error: The response is not a valid JSON.")
            return None

    @staticmethod
    def process_json_response(response):
        """
        Process the JSON response and return a markdown list.
        :param response: The response.
        :return: The markdown list.
        """
        try:
            response_json = PipelineUtils.parse_json_response(response)

            # Create a markdown list from the JSON data
            markdown_list = ""
            for key, items in response_json.items():
                markdown_list += f"**{key}**\n"
                for item in items:
                    markdown_list += f"\t- {item}\n"

            return markdown_list

        except json.JSONDecodeError:
            # If the response is not JSON, return the original text
            return response
