"""
This script is a simple AI Agent which will codify a piece text into Policies and Standards
"""

import json
from pipeline import Utils

def process_answer(answer, chatbot):
    """
    Process the answer received from the chatbot.
    """
    try:
        answer = answer.replace("```python", "").replace("```", "").strip()
        answer = json.loads(answer)
    except json.JSONDecodeError:
        print("\n\nThe answer is not a valid JSON.\n\n")
        print(answer)
        return

    stop = False
    for key in answer:
        try:
            print(f"\n\n{key}:")
            for value in answer[key]:
                response = chatbot.invoke(
                    "find all the requirements for" +
                    f" '{value}' " +
                    "in the content and format them as an ordered bullet list."
                )
                print(f"\n\n{value}:")
                print(response)
                print("\n--------------------------------------------\n")

                resp = input("Do you want to continue? (y/n): ").strip().lower()
                if resp == "n":
                    stop = True
                    break

            if stop:
                break

        except ValueError as e:
            print(f"\n\nError: {e}\n\n")
            break

def main():
    """
    Main function
    """
    try:
        args = Utils.get_args()
        chatbot = Utils.create_chatbot(args)

        answer = chatbot.invoke(
            "Which subjects are covered in the content?" +
            " Format the answer as a python Dictionary" +
            " and do not add any extra information to it."
        )

        process_answer(answer, chatbot)

        next_prompt = None
        while True:
            next_prompt = Utils.handle_command(
                input("\n** Enter your message: ") if next_prompt is None else next_prompt,
                chatbot
            )
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
