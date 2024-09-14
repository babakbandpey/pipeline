"""
Shared utility functions.
"""

import datetime
import os
import secrets
import sys
import argparse
from .config import OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY_1
from .rag_factory import RAGFactory
from .retrieval import Retrieval
from .chatbot_utils import logger


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
            default="gpt-4o-mini"
        )

        parser.add_argument(
            "--type",
            type=str,
            required=False,
            choices=[
            "chat",
            "txt",
            "python",
            "web",
            "pdf",
            "json",
            "md",
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
            '--output-path',
            type=str,
            required=False,
            help='Path to save the output file.',
        )

        parser.add_argument(
            "--url",
            type=str,
            required=False,
            help="URL to a website.",
            default=None
        )

        parser.add_argument(
            "--git_url",
			type=str,
			required=False,
			help="The url to a git repo to be used with the type PythonRAG",
			default=None)

        parser.add_argument(
            "--openai_api_key",
			type=str,
			required=False,
			default=OPENAI_API_KEY,
			help="OpenAI API key.")

        parser.add_argument(
            "--example",
			action="store_true" ,
			required=False,
			help="Showing some examples of how to run the script",
			default=None)

        parser.add_argument(
            "--prompt",
			type=str ,
			required=False,
			help="The prompt",
			default="Say something useful about the content")

        parser.add_argument(
            "--system_prompt_template",
            type=str ,
            required=False,
            help="The system prompt template",
            default=None)

        parser.add_argument(
            "--output_type",
            type=str ,
            required=False,
            help="The output type",
            default='text',
            choices=[
                "text",
                "json",
                'python',
                'xml',
                'html',
                'markdown'
            ])

        parser.add_argument(
            "--collection_name",
            type=str,
            required=False,
            help="The collection name",
            default=secrets.token_hex(16))

        parser.add_argument(
            "--auto_clean",
            action="store_true",
            required=False,
            help="Auto clean the non ascii characters",
            default=False)

        parser.add_argument(
            '--create-questionnaire',
            action='store_true',
            help='Create an questionnaire based on the created')

        parser.add_argument(
            '--remove-duplicates',
            action='store_true',
            help='Remove duplicates from the text')

        parser.add_argument(
            '--repair-md',
            action='store_true',
            help='Repare the markdown file')

        parser.add_argument(
            '--deep-organize',
            action='store_true',
            help='Deep organize the text')


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
            logger.info("Chat history saved to %s", filename)


        def default_action():
            logger.info("\n\n++Chatbot: %s", chatbot.invoke(prompt))


        def exit_chat():
            logger.info("\n\nGoodbye!\n\n")
            sys.exit(0)


        def show_history():
            """
            Show the chat history.
            :return: True if the chat history is shown, False otherwise.
            """
            if not chatbot.chat_history.messages:
                logger.info("No chat history.")
                return False

            for index, message in enumerate(chatbot.chat_history.messages):
                logger.info("%d. %s", index + 1, message)

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
                        logger.info("Message deleted.")
                    else:
                        logger.info("Invalid number provided.")
                else:
                    logger.info("Invalid number provided.")


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
    def print_examples():
        """ Print some examples of how to run the script. """
        print("""
            Examples:
            python .\\scripts\\run.py --type=chat or just python .\\scripts\\run.py
            python .\\scripts\\run.py --type=web --url=https://greydynamics.com/organisation-gladio/
            python .\\scripts\\run.py --type=txt --path=c:\\Users\\Me\\Documents\\policies
            python .\\scripts\\run.py --type=pdf --path=c:\\Users\\Me\\Documents\\policies
            python .\\scripts\\run.py --type=python --path=c:\\Users\\Me\\Documents\\project
        """)


    @staticmethod
    def get_base_url_and_api_key(args: argparse.Namespace) -> tuple[str, str]:
        """
        Get the base URL and the API key.
        :param args: The arguments.
        :return: The base URL and the API key.
        """

        url_endpoint = None
        openai_api_key = None

        if args.model == "llama3":
            url_endpoint, openai_api_key = "http://localhost:11434", None
        if args.model == "phi3":
            url_endpoint, openai_api_key = "http://localhost:11434", None
        if "gpt" in args.model:
            url_endpoint, openai_api_key = "https://api.openai.com/v1/", args.openai_api_key
        if "azure" in args.model:
            url_endpoint, openai_api_key = AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY_1
        if "lmstudio" in args.model:
            url_endpoint, openai_api_key = "http://localhost:1234/v1", "lm-studio"

        if url_endpoint is None:
            logger.error("Model not found for %s.", args.model)
            logger.info("Models: llama3, phi3, gpt-4o, gpt-4, gpt-3, azure, lmstudio")
            sys.exit(1)

        return url_endpoint, openai_api_key

    @staticmethod
    def get_kwargs(args: argparse.Namespace) -> dict:
        """
        Get the keyword arguments.
        :param args: The arguments.
        :return: The keyword arguments.
        """

        base_url, openai_api_key = PipelineUtils.get_base_url_and_api_key(args)

        _kwargs = {}

        for key, value in vars(args).items():
            _kwargs[key] = value

        _kwargs["base_url"] = base_url
        _kwargs["openai_api_key"] = openai_api_key

        return _kwargs


    @staticmethod
    def create_chatbot(args) -> Retrieval:
        """
        Create the chatbot.
        :param args: The arguments.
        :return: The chatbot.
        """

        if not args:
            args = PipelineUtils.get_args()
            args.type = "chat"

        logger.debug("Arguments: %s", args)

        if args.example:
            PipelineUtils.print_examples()
            sys.exit(0)

        kwargs = PipelineUtils.get_kwargs(args)

        if args.type == "py":
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            exclude_patterns = [
                "env/**/*",
                "env1/**/*",
                "venv/**/*",
                ".git/**/*",
                ".idea/**/*",
                ".vscode/**/*",
                "**/__pycache__/**/*",
                "**/.pytest_cache/**/*"
            ]
            exclude_paths = [os.path.join(base_path, pattern) for pattern in exclude_patterns]

            kwargs["exclude"] = exclude_paths

            return RAGFactory.get_rag_class("py", **kwargs)

        try:
            return RAGFactory.get_rag_class(args.type, **kwargs)
        except ValueError as exc:
            logger.error("Type not found for %s.", args.type)
            logger.info("Types: chat, txt, py, web, pdf, json")
            raise ValueError(f"Type not found for {args.type}.") from exc
