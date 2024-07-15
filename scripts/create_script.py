"""
Create script module
"""

from pipeline import PipelineUtils

def create_script(path:str, prompt:str):
    """
    Create a script by modifying the information inside
    the provided script based on the given information.

    Parameters:
    path (str): The path to the script file.
    prompt (str): The information to be used to modify the script.

    Returns:
    any: Depending on the output_type, the output will be returned.
    """

    # print the content of the script
    with open(path, 'r', encoding='utf-8') as file:
        print(file.read())

    # Define the template for the prompt to be used by the model.
    system_template = (
        "You are an LLM which has to change the information inside",
        "the script with the information provided.",
        "The returned file should be in Python and well formatted."
    )
    system_template = " ".join(system_template)

    args = PipelineUtils.get_args()
    args.type = 'py'
    args.path = path
    llm = PipelineUtils.create_chatbot(args)
    llm.setup_chat_prompt(system_template=system_template, output_type='python')
    # Invoke the chain with the provided text and info to get the modified script.
    answer = llm.invoke(prompt)

    llm.logger.info(answer)

    return answer


def main():
    """
    The main function.
    """
    # Define the script content.
    # read the file from the root directory/tests/test.py

    path = './tests/data/test.py'
    create_script(path, "Write a test case for each method in the test.py.")


if __name__ == "__main__":
    main()
