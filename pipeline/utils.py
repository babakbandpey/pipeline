"""
Shared utility functions.
"""

import datetime
import os
import sys
import argparse
from pipeline import OPENAI_API_KEY
from pipeline import Chatbot, TextRAG, PythonRAG, WebRAG, PdfRAG

class PipelineUtils():
    """ Utility class for the pipeline. """

    @staticmethod
    def get_args():
        """
        Get the arguments.
        :return: The arguments.
        """

        parser = argparse.ArgumentParser(description="Run chatbot with different configurations.")
        parser.add_argument("--model", type=str, required=False, help="Model to use.", default="gpt-4o")
        parser.add_argument("--type", type=str, required=False, choices=[
            "chat",
            "text",
            "python",
            "web",
            "pdf",
            "scraper",
            'search'
            ], help="Class type to use.", default="chat")
        parser.add_argument("--path", type=str, required=False, help="Local path to a file or directory.", default=None)
        parser.add_argument("--url", type=str, required=False, help="URL to a website.", default=None)
        parser.add_argument("--git_url", type=str, required=False, help="The url to a git repo to be used with the type PythonRAG", default=None)
        parser.add_argument("--openai_api_key", type=str, required=False, default=OPENAI_API_KEY, help="OpenAI API key.")
        parser.add_argument("--example", action="store_true" , required=False, help="Showing some examples of how to run the script", default=None)
        parser.add_argument("--prompt", type=str , required=False, help="The prompt", default="Say something useful about the content")
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
            --------------------------------------------------------------------------------
            The following types have no memory:
            python .\\scripts\\run.py --type=scraper --url=https://greydynamics.com/organisation-gladio/
            python .\\scripts\\run.py --type=scraper --path=file://c:\\Users\\Me\\Documents\\project
                    The above returns JSON output
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

        if args.type == "chat":
            return Chatbot(
                base_url=base_url,
                model=args.model,
                openai_api_key=openai_api_key
            )

        if args.type == "text":
            return TextRAG(
                base_url=base_url,
                model=args.model,
                openai_api_key=openai_api_key,
                path=args.path
            )

        if args.type == "python":
            # if args.path is not a directory and
            # the args.git_url is None the exclude path is not needed
            if not os.path.isdir(args.path) and args.git_url is None:
                return PythonRAG(
                    base_url=base_url,
                    model=args.model,
                    path=args.path,
                    openai_api_key=openai_api_key
                )

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
            return PythonRAG(
                base_url=base_url,
                model=args.model,
                path=args.path,
                git_url=args.git_url,
                openai_api_key=openai_api_key,
                exclude=exclude_paths
            )

        if args.type == "web":
            return WebRAG(
                base_url=base_url,
                model=args.model,
                url=args.url,
                openai_api_key=openai_api_key
            )

        if args.type == "pdf":
            return PdfRAG(
                base_url=base_url,
                model=args.model,
                path=args.path,
                openai_api_key=openai_api_key
            )

        if args.type == "scraper":
            return Scraper(
                base_url=base_url,
                model=args.model,
                url=args.url,
                openai_api_key=openai_api_key,
                prompt=args.prompt
            )

        if args.type == "search":
            return Search(
                model=args.model,
                openai_api_key=openai_api_key,
                prompt=args.prompt,
                base_url=base_url
            )


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