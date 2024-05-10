# https://python.langchain.com/docs/use_cases/chatbots/memory_management/

import sys
import datetime
from libs.pipeline import ChatbotPipeline, WebRetrievalPipeline


def main():
    """
    The main function.
    """

if __name__ == "__main__":

    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    # pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")
    pipeline = WebRetrievalPipeline(base_url="http://localhost:11434", model="llama3", url = "https://python.langchain.com/v0.1/docs/use_cases/chatbots/memory_management/")
    try:
        while True:
            prompt = input("\n** Enter your message: ")
            if prompt == "/exit":
                print("\n\nGoodbye!\n\n")
                sys.exit(0)
            if prompt == "/reset":
                pipeline.clear_chat_history()
                continue
            if prompt == "/history":
                for index, message in enumerate(pipeline.chat_history.messages):
                    print(f"{index + 1}. {message}")

                if len(pipeline.chat_history.messages) == 0:
                    print("No chat history.")
                continue
            if "/delete" in prompt:
                index = int(prompt.split(" ")[1])
                pipeline.modify_chat_history(index - 1)
                continue
            print("\n\n++Chatbot: ", pipeline.invoke(prompt))
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")
        sys.exit(0)
