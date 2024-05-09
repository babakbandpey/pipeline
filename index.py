# https://python.langchain.com/docs/use_cases/chatbots/memory_management/

import sys
import datetime
from libs.chatbot_pipeline import ChatbotPipeline


def main():
    """
    The main function.
    """

if __name__ == "__main__":
    pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")
    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")
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

    # loader = pipeline.web_base_loader('https://www.cnn.com/')
    # text_splitter = pipeline.recursive_character_text_splitter()
    # full_chain = pipeline.process_data(loader, text_splitter)
    # pipeline.query_chain(full_chain, "What are the most important news on CNN.com?")
