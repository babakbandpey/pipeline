import sys
import os
import datetime
from libs.pipeline import ChatbotPipeline, WebRetrievalPipeline


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


def handle_command(prompt: str, pipeline: ChatbotPipeline):
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
    # url = "https://python.langchain.com/v0.1/docs/use_cases/chatbots/memory_management/"

    pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")
    # pipeline = WebRetrievalPipeline(
    #     base_url="http://localhost:11434",
    #     model="llama3",
    #     url=url
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
