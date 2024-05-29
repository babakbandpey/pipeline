"""
file ./run.py
author: Babak Bandpey
This file is made to try out the classes.
"""

import datetime
from utils import handle_command, get_args, create_chatbot


def main():
    """
    The main function.
    """
    # write the date and the time of the conversation
    print("\n\nWelcome to the chatbot!\n\n")
    print("Today's date and time: ", datetime.datetime.now(), "\n\n")

    next_prompt = None


    args = get_args()
    chatbot = create_chatbot(args)

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
