# https://python.langchain.com/docs/use_cases/chatbots/memory_management/

import os
import datetime
from libs.pipeline import ChatbotPipeline, WebRetrievalPipeline


def handle_command():
    """
    Handle the command.
    """

    if prompt == "/reset":
        pipeline.clear_chat_history()
        return "/history"
    elif prompt == "/history":
        history = pipeline.chat_history.messages
        if history:
            for index, message in enumerate(history):
                print(f"{index + 1}. {message}")
        else:
            print("No chat history.")
    elif "/delete" in prompt:
        try:
            index = int(prompt.split()[1])
            pipeline.modify_chat_history(index - 1)
        except (IndexError, ValueError):
            print("Invalid index provided.")
        return "/history"
    elif prompt == "/summarize":
        pipeline.summarize_messages()
        return "/history"
    elif prompt == "/save":
        # save the chat history to a file called
        # chat_history_<datetime>.md under the ./history folder
        history = pipeline.chat_history.messages

        # check if the history folder exists, if not, create it
        if not os.path.exists("history"):
            os.makedirs("history")

        filename = os.path.join(
            "history",
            f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        with open(filename, "w", encoding='utf-8') as file:
            for index, message in enumerate(history):
                file.write(f"{index + 1}. {message}\n")

    elif prompt == "/help":
        print_commands_help()
        return None
    return None


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

if __name__ == "__main__":

    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")
    # pipeline = WebRetrievalPipeline(
    #     base_url="http://localhost:11434",
    #     model="llama3",
    #     url="https://python.langchain.com/v0.1/docs/use_cases/chatbots/memory_management/"
    # )

    NEXT_PROMPT = None

    try:
        while True:
            prompt = input("\n** Enter your message: ") if 'NEXT_PROMPT' not in globals() or NEXT_PROMPT is None else NEXT_PROMPT
            NEXT_PROMPT = None

            if prompt == "/exit":
                print("\n\nGoodbye!\n\n")
                break

            next_action = handle_command()
            if next_action:
                NEXT_PROMPT = next_action
            else:
                print("\n\n++Chatbot: ", pipeline.invoke(prompt))

    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")
