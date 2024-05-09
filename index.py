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

    pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")
    try:
        while True:
            prompt = input("Enter your message: ")
            if prompt == "/exit":
                print("\n\nGoodbye!\n\n")
                sys.exit(0)
            if prompt == "/reset":
                pipeline.clear_chat_history()
                continue
            if prompt == "/history":
                print(pipeline.chat_history.messages)
                continue
            print(pipeline.invoke(prompt))
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")
        sys.exit(0)


    # pipeline = WebRetrievalPipeline(base_url="http://localhost:11434", model="llama3", url = "https://www.cnn.com/")

    # try:
    #     while True:
    #         prompt = input("Enter your message: ")
    #         if prompt == "/exit":
    #             print("\n\nGoodbye!\n\n")
    #             sys.exit(0)
    #         if prompt == "/reset":
    #             pipeline.clear_chat_history()
    #             continue
    #         if prompt == "/history":
    #             print(pipeline.chat_history.messages)
    #             continue
    #         print(pipeline.invoke(prompt))
    # except KeyboardInterrupt:
    #     print("\n\nGoodbye!\n\n")
    #     sys.exit(0)
