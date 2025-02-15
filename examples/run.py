"""
file ./run.py
author: Babak Bandpey
This file is made to try out the classes.
"""

import datetime
from pipeline import PipelineUtils

def main():
    """
    The main function.
    """
    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    next_prompt = None

    args = PipelineUtils.get_args()
    chatbot = PipelineUtils.create_chatbot(args)

    try:
        while True:
            next_prompt = PipelineUtils.handle_command(
                input("\n** Enter your message: ") if next_prompt is None else next_prompt,
                chatbot
            )
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
