"""
This script is a simple AI Agent which will codify a piece text into Policies and Standards
"""

import json
from utils import handle_command, get_args, create_chatbot

def main():
    """
    Main function
    """
    try:
        args = get_args()
        chatbot = create_chatbot(args)

        answer = chatbot.invoke(
            "Which subjects are covered in the content?" +
            " Format the answer as a python Dictionary" +
            " and do not add any extra information to it."
        )

        answer = answer.replace("```python", "").replace("```", "").strip()

        try:
            # converting the answer to JSON
            answer = json.loads(answer)
            print(answer)
        except json.JSONDecodeError:
            print("\n\nThe answer is not a valid JSON.\n\n")
            print(answer)
            return

        # for each key in the answer print the key and loop through the values

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

                    resp = input("Do you want to continue? (y/n): ")
                    if resp.lower() == "n":
                        stop = True
                        break

                if stop:
                    break

            except ValueError as e:
                print(f"\n\nError: {e}\n\n")
                break

        next_prompt = None
        while True:
            next_prompt = handle_command(
                input("\n** Enter your message: ") if next_prompt is None else next_prompt,
                chatbot
            )
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n\n")


if __name__ == "__main__":
    main()
