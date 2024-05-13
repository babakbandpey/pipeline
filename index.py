import sys
import os
import datetime
from pipeline.chatbot import Chatbot
from pipeline.web_rag import WebRAG
from pipeline.python_rag import PythonRAG

# BASE_URL="http://localhost:11434",
# MODEL="llama3"

# BASE_URL="http://localhost:11434",
# MODEL="phi3"

BASE_URL = "http://localhost:1234/v1"
MODEL = None

def save_chat_history(pipeline):
    """
    Save the chat history.
    :param pipeline: The pipeline.
    """

    if not os.path.exists("history"):
        os.makedirs("history")
    filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = os.path.join("history", filename)
    with open(path, "w", encoding='utf-8') as file:
        for index, message in enumerate(pipeline.chat_history.messages):
            file.write(f"{index + 1}. {message}\n")
    print(f"Chat history saved to {filename}")


def handle_command(prompt: str, pipeline: Chatbot):
    """
    Handle the command.
    :param prompt: The prompt.
    :param pipeline: The pipeline.
    """

    def default_action():
        print("\n\n++Chatbot: ", pipeline.invoke(prompt))

    def exit_chat():
        print("\n\nGoodbye!\n\n")
        sys.exit(0)

    def show_history():
        """
        Show the chat history.
        :return: True if the chat history is shown, False otherwise.
        """
        if not pipeline.chat_history.messages:
            print("No chat history.")
            return False

        for index, message in enumerate(pipeline.chat_history.messages):
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
                if pipeline.modify_chat_history(number - 1):
                    print("Message deleted.")
                else:
                    print("Invalid number provided.")
            else:
                print("Invalid number provided.")

    commands = {
        "/exit": exit_chat,
        "/reset": lambda: (pipeline.clear_chat_history(), "/history")[1],
        "/history": lambda: (show_history(), None)[1],
        "/delete": lambda: (delete_message(), "/history")[1],
        "/summarize": lambda: (pipeline.summarize_messages(), "/history")[1],
        "/save": lambda: save_chat_history(pipeline),
        "/help": print_commands_help
    }

    # Retrieve the function from the dictionary and call it, if not found, call default_action
    action = commands.get(prompt, default_action)
    return action()


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
          /help
          """
    )


def main():
    """
    The main function.
    """
    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    next_prompt = None


    # pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")

    url = "https://python.langchain.com/v0.1/docs/use_cases/code_understanding/"
    pipeline = WebRAG(
        base_url=BASE_URL,
        model=MODEL,
        url=url
    )

    # pipeline = PythonRAG(
    #     base_url="http://localhost:11434",
    #     model="llama3",
    #     path='/home/bba/0-projects/pipeline/pipeline/pipeline.py',
    # )

    try:
        while True:
            next_prompt = handle_command(
                input("\n** Enter your message: ") if next_prompt is None else next_prompt,
                pipeline
            )
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
