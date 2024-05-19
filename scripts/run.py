"""
file ./run.py
author: Babak Bandpey
This file is made to try out the classes.
"""

import sys
import os
import datetime

from src import OPENAI_API_KEY, Chatbot, TextRAG, PythonRAG, WebRAG

# Ollama
# BASE_URL="http://localhost:11434"
# MODEL="llama3"
# OPENAI_API_KEY = None

# Ollama
# BASE_URL="http://localhost:11434",
# MODEL="phi3"
# OPENAI_API_KEY = None

# LM Studio
# BASE_URL = "http://localhost:1234/v1"
# MODEL = None
# OPENAI_API_KEY = None

# OPENAI
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"



def handle_command(prompt: str, chatbot: Chatbot):
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
        "/reset": lambda: (chatbot.clear_chat_history(), "/history")[1],
        "/history": lambda: (show_history(), None)[1],
        "/delete": lambda: (delete_message(), "/history")[1],
        "/summarize": lambda: (chatbot.summarize_messages(), "/history")[1],
        "/save": save_chat_history,
        "/help": print_commands_help
    }

    # Retrieve the function from the dictionary and call it, if not found, call default_action
    action = commands.get(prompt, default_action)
    return action()


def main():
    """
    The main function.
    """
    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    next_prompt = None

    # chatbot = Chatbot(base_url="http://localhost:11434", model="llama3")
    # chatbot = Chatbot(base_url=BASE_URL, model=MODEL, openai_api_key=OPENAI_API_KEY)

    # url = "https://python.langchain.com/v0.1/docs/use_cases/code_understanding/"
    # chatbot = pipeline.WebRAG(
    #     base_url=BASE_URL,
    #     model=MODEL,
    #     url=url,
    #     openai_api_key=OPENAI_API_KEY
    # )

    # base_path = os.getcwd()

    # exclude_patterns = [
    #     "env/**/*",
    #     "venv/**/*",
    #     ".git/**/*",
    #     ".idea/**/*",
    #     ".vscode/**/*",
    #     "**/__pycache__/**/*",
    #     "**/.pytest_cache/**/*"
    # ]

    # # Convert to absolute paths for base_path specific directories
    # exclude_paths = [os.path.join(base_path, pattern) for pattern in exclude_patterns]

    # print("Excluded paths: ", exclude_paths)

    # chatbot = PythonRAG(
    #     base_url=BASE_URL,
    #     model=MODEL,
    #     path=os.path.join(base_path, "pipeline"),
    #     openai_api_key=OPENAI_API_KEY,
    #     exclude=exclude_paths
    # )

    chatbot = TextRAG(
        base_url=BASE_URL,
        model=MODEL,
        openai_api_key=OPENAI_API_KEY,
        path='C:\\Users\\M106026\\Documents\\policies'
    )

    try:
        while True:
            next_prompt = handle_command(
                input("\n** Enter your message: ") if next_prompt is None else next_prompt,
                chatbot
            )
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
