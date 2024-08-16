"""
This script reads file's content and organizes it in a structured way.
"""

import argparse
import datetime
import json
import os
from typing import Union
from pipeline import PipelineUtils, FileUtils, ChatbotUtils, logger

def analyzer(chatbot, prompt: str) -> Union[dict, str]:
    """
    Analyzes a single file and writes the results to the output file.
    :param chatbot: Chatbot object of the classes TextRAG or PdfRAG
    :param prompt: Prompt to be analyzed
    :return: JSON response
    """

    logger.info("prompt %s...", prompt)

    response = chatbot.invoke(
        f"""
        {prompt}
        Format the output as JSON.
        Example: {{"areas_covered": [List of the areas covered by the content]}}
        """
    )

    logger.info("response %s...", response)

    return ChatbotUtils.parse_json(response)


def get_output_file(file: str) -> str:
    """
    Get the output file name based on the input file.
    :param file: Input file
    :return: Output file
    """

    return (
        f"{file.replace(' ', ' ').replace('.pdf', '').replace('.txt', '')}-"
        f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )


def organize_content(args, output_file, create_questionnaire=False):
    """
    Main function to organize the content of files.
    :param args: Arguments passed to the script
    :param create_questionnaire: Create an questionnaire based on the analysis of the content
    """

    files = FileUtils.get_files(args.path, f".{args.type}")

    for file in files:
        # Create an output file with timestamp .md file and write the response to it
        print(f"Processing file: {file}")

        args.collection_name = f"organizer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chatbot = PipelineUtils.create_chatbot(args)

        logger.info("............................................")
        # Get absolute path of the file

        prompt = (
            "Analyze content and make a prioritized list of which areas it covers "
            "based on what is important for Cybersecurity, Business Continuity and Disaster Recovery."
        )
        topics = analyzer(chatbot, prompt)

        for i, area in enumerate(topics['areas_covered']):
            FileUtils.write_to_file(output_file, f"## {i + 1} - {area}\n\n", mode='a')

            prompt= f"""
            List every relevant requirements needed to comply with '{area}'.
            If the requirements are repeated, there should be a good reason for mentioning them again.
            The list should be prioritized based on the importance of the requirements.
            If possible improve, optimize and modenize the requirements to match the current standards and best practices.
            If the requirement is essential, it should star with a +.
            If the requirement is nice to have, it should start with a %.
            """
            requirements = analyzer(chatbot, prompt)
            for key in requirements:
                for z, requirement in enumerate(requirements[key]):
                    output = ChatbotUtils.process_json_response(requirement)
                    if output.startswith(" - "):
                        FileUtils.write_to_file(output_file, f"{output}\n", mode='a')
                    else:
                        FileUtils.write_to_file(output_file, f"**{i + 1}.{z + 1}:** {output}\n", mode='a')

                    if create_questionnaire:
                        yield area, requirement


        # Get the purpose of the policies and the requirements
        prompt = "Write the purpose of the policies and the requirements in a few sentences."
        purpose = analyzer(chatbot, prompt)

        FileUtils.prepend_to_file(output_file, f"# Purpose\n\n{purpose['purpose']}\n\n")

        # Get a description of the content
        prompt = "Summarize the content in a few sentences."
        summary = analyzer(chatbot, prompt)

        FileUtils.prepend_to_file(output_file, f"# Summary\n\n{summary['summary']}\n\n")

        chatbot.delete_collection()
        chatbot.clear_chat_history()

        logger.info("::::::::::::::::::::::::::::::::::::::::::::")


def create_questionnaire(area, requirement, output_file):
    """
    Create a questionnaire based on the area and requirements.
    the requirements should be converted to questions.
    The whole thing should be collected in a json object and saved to a file, which has the same name as the output file but with a .json extension.
    The file should be updated for each area and requirements.
    the questions should be generated using a prompt and the chatbot.

    the json object should look like this:
    {
        area1: [
            question1,
            question2,
            ...
        ],
        area2: [
            question1,
            question2,
            ...
        ],
        ...


    :param area: Area to be covered
    :param requirements: Requirements to be covered
    """
    try:
        logger.debug("Creating questionnaire for area '%s' and requirement '%s'...", area, requirement)
        chatbot = PipelineUtils.create_chatbot(None)
        logger.debug("Chatbot created...")
        json_file = output_file.replace('.md', '.json')

        # Generate questions based on requirements

        prompt = f"""
        Convert the requirement '{requirement}' into a question.
        The question should be ask to the person who is responsible for the requirement.
        Like does the company have a policy for '{requirement}'? If yes, what is the policy?
        or Do have a procedure for '{requirement}'? If yes, what is the procedure?
        or Do you have a process for '{requirement}'? If yes, what is the process?
        etc.
        """
        question = chatbot.invoke(prompt)

        logger.info("Question: %s", question)

        # Check if the file exists
        if os.path.exists(json_file):
            # Load the existing questionnaire
            with open(json_file, 'r') as file:
                existing_questionnaire = json.load(file)

            # Check if the area already exists in the questionnaire
            if area in existing_questionnaire:
                # Add the question to the existing area
                existing_questionnaire[area].append(question)
            else:
                # Add the area and question to the questionnaire
                existing_questionnaire[area] = [question]

            # Save the updated questionnaire to the file
            FileUtils.write_to_file(json_file, json.dumps(existing_questionnaire))
        else:
            # Create a new questionnaire
            questionnaire = {area: [question]}
            FileUtils.write_to_file(json_file, json.dumps(questionnaire))
    except Exception as e:
        logger.error("Error creating questionnaire: %s", e)
        raise e


def convert_json_to_md(output_file):
    """
    Convert a JSON file to a markdown file.
    :param json_file: JSON file to be converted
    :param output_file: Output markdown file
    """

    json_file = output_file.replace('.md', '.json')

    # Load the JSON file
    with open(json_file, 'r') as file:
        questionnaire = json.load(file)

    # Write the questionnaire to the output file
    for area in questionnaire:
        FileUtils.write_to_file(output_file, f"## {area}\n\n", mode='a')
        for i, question in enumerate(questionnaire[area]):
            FileUtils.write_to_file(output_file, f"**{i + 1}:** {question}\n", mode='a')


def convert_md_to_docx(output_file):
    """
    Convert a markdown file to a docx file.
    :param output_file: Output markdown file
    """

    docx_file = output_file.replace('.md', '.docx')

    # Convert the markdown file to a docx file
    os.system(f"pandoc {output_file} -o {docx_file}")

    logger.info("Docx file created: %s", docx_file)

def main():
    """Entry point for the script."""

    args = PipelineUtils.get_args()

    if args.type not in ['pdf', 'txt']:
        logger.error("The type should be 'pdf' or 'txt'.")
        raise ValueError("The type should be 'pdf' or 'txt'.")


    try:

        output_file = get_output_file(args.path)

        if args.create_questionnaire:

            for area, requirement in organize_content(args, output_file, True):
                logger.info("Creating questionnaire for area '%s' and requirement '%s'...", area, requirement)
                create_questionnaire(area, requirement, output_file)

            convert_json_to_md(output_file)
        else:
            organize_content(args, output_file, False)

        convert_md_to_docx(output_file)

    except KeyboardInterrupt:
        logger.info("Exiting the script...")
    except Exception as e:
        logger.error("Error organizing content: %s", e)
        raise e

if __name__ == "__main__":
    main()
