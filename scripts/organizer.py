"""
This script reads file's content and organizes it in a structured way.
"""

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


def get_output_file(path: str) -> str:
    """
    Get the output file name based on the input file or folder.
    If the input is a file, the output will be based on the file name.
    If the input is a folder, the output will be based on the last folder in the path.
    :param file: Input file or folder
    :return: Output file with full path
    """

    # Check if the file or folder exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file or folder '{path}' does not exist.")

    # Check if the input is a directory or a file
    if os.path.isdir(path):
        # Extract the last folder name from the path
        folder_name = os.path.basename(os.path.normpath(path))
        # Join the folder path and file name
        return os.path.join(path, f"{folder_name}-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    else:
        # It's a file, so return based on the file name
        folder_path = os.path.dirname(path)
        file_name = os.path.basename(path).replace(".pdf", "").replace(".txt", "")
        return os.path.join(folder_path, f"{file_name}-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")



def organize_content(args, output_file, create_questionnaire=False):
    """
    Main function to organize the content of files.
    :param args: Arguments passed to the script
    :param create_questionnaire: Create a questionnaire based on the analysis of the content
    """

    # Get all files
    files = FileUtils.get_files(args.path, f".{args.type}")

    # List to store all requirements (for both cases of create_questionnaire)
    all_requirements = []


    for file in files:

        content = []

        # Extract the file name, remove extensions, and replace dashes with spaces
        subject = os.path.basename(file).replace("-", " ").replace(".pdf", "").replace(".txt", "")

        content.append(f"# {subject}\n\n")

        # Write the file name as the title at the top of the markdown file
        # FileUtils.write_to_file(output_file, f"# {file_name}\n\n", mode='a')

        # Create an output file with timestamp and write the response to it
        print(f"Processing file: {file}")

        args.collection_name = f"organizer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chatbot = PipelineUtils.create_chatbot(args)

        logger.info("............................................")

        # First prompt: Analyze content
        prompt = (
            "Analyze content and make a prioritized list of which areas it covers "
            "based on what is important for Cybersecurity, Business Continuity and Disaster Recovery."
        )
        response_topics = analyzer(chatbot, prompt)

        for i, area in enumerate(response_topics['areas_covered']):
            content.append(f"## {i + 1} - {area}\n\n")

            # Second prompt: List relevant requirements
            prompt = f"""
            List every relevant requirement needed to comply with '{area}'.
            If no content is found in knowledge base, write requirements based on your knowledge about "{area}" related to "{subject}" in domain of Cybersecurity.
            List should be prioritized based on importance of requirements.
            Keep same tone and same style of writing and do not change meaning of requirements.
            Response in json format.
            format of response should be like this:
            {{
                "requirements": [
                    "Requirement 1",
                    "Requirement 2",
                    "Requirement 3",
                    ........
                ],
            }}
            """.replace("  ", "")

            response_requirements = analyzer(chatbot, prompt)

            if 'requirements' not in response_requirements:
                logger.error(f"No requirements found in the response for the area: '{area}' for the subject: '{subject}'.")
                raise ValueError(f"No requirements found in the response for the area: '{area}' for the subject '{subject}' .")

            requirements = response_requirements['requirements']  # Extract the 'requirements' list from the response

            for z, requirement in enumerate(requirements):
                logger.info(f"Requirement: {requirement}")

                output = ChatbotUtils.process_json_response(requirement)

                if output.startswith(" - "):
                    content.append(f"{output}\n\n")
                else:
                    content.append(f"**{z + 1}:** {output}\n\n")

                # Add to all_requirements if create_questionnaire is True
                if create_questionnaire:
                    all_requirements.append((z + 1, requirement))


        content.append("\\newpage\n\n")

        # Inserting a table of contents at the top of the file
        content.insert(0, f"\\toc\n\\newpage")

        # Get the purpose of the policies and the requirements
        prompt = "Write the purpose of the policies and the requirements in a few sentences."
        purpose = analyzer(chatbot, prompt)
        content.insert(1, f"## Purpose\n\n{purpose['purpose']}\n\n")

        # Get a description of the content
        prompt = "Summarize the content in a few sentences."
        summary = analyzer(chatbot, prompt)
        content.insert(2, f"## Summary\n\n{summary['summary']}\n\n")

        FileUtils.write_to_file(output_file, "".join(content), mode='a')

        # Clean up the chatbot collection and history
        chatbot.delete_collection()
        chatbot.clear_chat_history()

        logger.info("::::::::::::::::::::::::::::::::::::::::::::")

    return all_requirements if create_questionnaire else None


def deep_organizer(args, output_file, create_questionnaire=False):
    """
    Main function to organize the content of files.
    :param args: Arguments passed to the script
    :param create_questionnaire: Create a questionnaire based on the analysis of the content
    """

    # Get all files
    files = FileUtils.get_files(args.path, f".{args.type}")

    # List to store all requirements (for both cases of create_questionnaire)
    all_requirements = []


    for file in files:

        content = []

        # Extract the file name, remove extensions, and replace dashes with spaces
        subject = os.path.basename(file).replace("-", " ").replace(".pdf", "").replace(".txt", "")

        content.append(f"% {subject}\n\n")

        # Write the file name as the title at the top of the markdown file
        # FileUtils.write_to_file(output_file, f"# {file_name}\n\n", mode='a')

        # Create an output file with timestamp and write the response to it
        print(f"Processing file: {file}")

        args.collection_name = f"deep_organizer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chatbot = PipelineUtils.create_chatbot(args)

        logger.info("............................................")

        prompt = (
            "Analyze content and make a list of which policies it covers. "
            "Find the title of the policies and write them in a list. "
            "The format of the response should be like this: "
            "{"
            "    'policies': ["
            "        'Policy 1',"
            "        'Policy 2',"
            "        'Policy 3',"
            "        ........"
            "    ]"
            "}"
        )

        response_policies = analyzer(chatbot, prompt)

        logger.info("Policies: %s", response_policies['policies'])

        for i, policy in enumerate(response_policies['policies']):

            content.append(f"# {i + 1} - {policy}\n\n")

            # Second prompt: Analyze content

            prompt = f"Analyze content and make a prioritized list of which areas it covers for policy '{policy}'."

            response_topics = analyzer(chatbot, prompt)

            for i, area in enumerate(response_topics['areas_covered']):
                content.append(f"## {i + 1} - {area}\n\n")

                # Second prompt: List relevant requirements
                prompt = f"""
                List every relevant requirement needed to comply with '{area}'.
                If no content is found in knowledge base, write requirements based on your knowledge about "{area}" related to "{subject}" in domain of Cybersecurity.
                List should be prioritized based on importance of requirements.
                Keep same tone and same style of writing and do not change meaning of requirements.
                Response in json format.
                format of response should be like this:
                {{
                    "requirements": [
                        "Requirement 1",
                        "Requirement 2",
                        "Requirement 3",
                        ........
                    ],
                }}
                """.replace("  ", "")

                response_requirements = analyzer(chatbot, prompt)

                if 'requirements' not in response_requirements:
                    logger.error(f"No requirements found in the response for the area: '{area}' for the subject: '{subject}'.")
                    raise ValueError(f"No requirements found in the response for the area: '{area}' for the subject '{subject}' .")

                requirements = response_requirements['requirements']  # Extract the 'requirements' list from the response

                for z, requirement in enumerate(requirements):
                    logger.info(f"Requirement: {requirement}")

                    output = ChatbotUtils.process_json_response(requirement)

                    if output.startswith(" - "):
                        content.append(f"{output}\n\n")
                    else:
                        content.append(f"**{z + 1}:** {output}\n\n")

                    # Add to all_requirements if create_questionnaire is True
                    if create_questionnaire:
                        all_requirements.append((z + 1, requirement))


            content.append("\\newpage\n\n")

            content.insert(0, f"\\toc\n\\newpage")

            # Get the purpose of the policies and the requirements
            prompt = "Write the purpose of the policies and the requirements in a few sentences."
            purpose = analyzer(chatbot, prompt)
            content.insert(1, f"## Purpose\n\n{purpose['purpose']}\n\n")

            # Get a description of the content
            prompt = "Summarize the content in a few sentences."
            summary = analyzer(chatbot, prompt)
            content.insert(2, f"## Summary\n\n{summary['summary']}\n\n")

            FileUtils.write_to_file(output_file, "".join(content), mode='a')

        # Clean up the chatbot collection and history
        chatbot.delete_collection()
        chatbot.clear_chat_history()

        logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

    return all_requirements if create_questionnaire else None


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

    if not os.path.exists(output_file):
        logger.error("The output file does not exist: %s", output_file)
        raise FileNotFoundError("The output file does not exist.")

    docx_file = output_file.replace('.md', '.docx')

    logger.info(f"Converting markdown file to docx file: {output_file} -> {docx_file}")
    # Convert the markdown file to a docx file
    os.system(f"pandoc {output_file} --filter=pandoc-docx-pagebreakpy -o {docx_file}")

    logger.info("Docx file created: %s", docx_file)


def convert_md_to_pdf(output_file):
    """
    Convert a markdown file to a pdf file.
    :param output_file: Output markdown file
    """

    if not os.path.exists(output_file):
        logger.error("The output file does not exist: %s", output_file)
        raise FileNotFoundError("The output file does not exist.")

    pdf_file = output_file.replace('.md', '.pdf')

    logger.info(f"Converting markdown file to pdf file: {output_file} -> {pdf_file}")
    # Convert the markdown file to a pdf file
    os.system(f"pandoc {output_file} -o {pdf_file}")

    logger.info("Pdf file created: %s", pdf_file)


def remove_duplicates(args, output_file):
    """
    Remove duplicate requirements from the output file.
    :param args: Arguments passed to the script
    :param output_file: Output file
    """

    # Get all files
    files = FileUtils.get_files(args.path, f".{args.type}")

    print(f"Removing duplicates from {len(files)} files... {files}")

    for file in files:
        # Extract the file name, remove extensions, and replace dashes with spaces
        file_name = os.path.basename(file).replace("-", " ").replace(".pdf", "").replace(".txt", "")

        # Write the file name as the title at the top of the markdown file
        FileUtils.write_to_file(output_file, f"# {file_name}\n\n", mode='a')

        # Create an output file with timestamp and write the response to it
        logger.info(f"Processing file: {file}")

        args.collection_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"


        args.system_prompt_template = """
Your are a text analyst and you have to analyze the content of the file.
the response should be in JSON format.
Examples:
{{
  "LogManagementPolicy": {{
    "Purpose": "To establish a comprehensive framework for logging data to support the identification, investigation, and response to information security incidents while ensuring the integrity and confidentiality of log data.",
    "Scope": "This policy applies to all IT devices, applications, and systems within the organization that generate logs.",
    "PolicyStatement": {{
      "LoggingRequirements": {{
        "EventLogs": "All user activities, exceptions, faults, and security events must be logged and retained for a minimum of 90 days.",
        "LogTypes": {{
          "SystemLogs": {{
            "Description": "Default logs generated by systems.",
            "Retention": "Minimum of 90 days.",
            "Modification": "Must remain unchanged."
          }},
          "ApplicationLogs": {{
            "Description": "Custom logs generated by applications.",
            "Retention": "Minimum of 90 days, subject to business needs.",
            "Modification": "Post-log enrichment is permitted."
          }},
          "AuditLogs": {{
            "Description": "Logs that meet specific audit requirements.",
            "Retention": "Minimum of 90 days.",
            "Modification": "Must remain unchanged."
          }}
        }}
      }},
      "LogProtection": {{
        "AccessControl": "Access to logs must be restricted based on role-based access control (RBAC).",
        "Integrity": "Logs must be protected from unauthorized modification or deletion.",
        "Confidentiality": "Logs must be classified as confidential and stored securely."
      }},
      "LogCollection": {{
        "CentralLogRepository": "All logs must be collected in a centralized log repository for analysis and monitoring.",
        "SIEMIntegration": "Logs must be integrated with Security Information and Event Management (SIEM) systems for real-time threat detection."
      }},
      "LogTransfer": {{
        "RealTimeTransfer": "Logs must be transferred in real-time to enable timely analysis.",
        "Encryption": "Logs must be encrypted during transfer over insecure networks."
      }},
      "MonitoringAndReview": {{
        "RegularReview": "Logs must be reviewed at least monthly to identify abnormal patterns and potential threats.",
        "IncidentResponse": "Log data must support incident response activities and forensic analysis."
      }},
      "Training": {{
        "StakeholderTraining": "All relevant personnel must receive training on log management processes and best practices."
      }},
      "Exceptions": {{
        "Process": "Any deviations from this policy must follow the established exception process, including risk assessment and mitigation planning."
      }}
    }},
    "Compliance": {{
      "Standards": "This policy aligns with ISO/IEC 27002:2022 and other relevant regulatory requirements."
    }}
  }}
}}

You can change the keys and values to match the content of the file.
You can use camelCase or snake_case or ordinary case for the keys.
"""

        chatbot = PipelineUtils.create_chatbot(args)

        logger.info("............................................")

        # First prompt: Analyze content
        prompt = (
            "Analyze content and make a prioritized list of which areas it covers "
            "based on what is important for Cybersecurity, Business Continuity and Disaster Recovery."
        )
        topics = analyzer(chatbot, prompt)

        for i, area in enumerate(topics['areas_covered']):
            FileUtils.write_to_file(output_file, f"## {i + 1} - {area}\n\n", mode='a')

            # Second prompt: List relevant requirements
            prompt = f"""
            write the policy about the topic '{area}'.
            If possible improve, optimize and modernize the text to match the current standards and best practices.
            Avoid redundant and duplicate information, unless it is necessary and relevant.
            """.replace("  ", "")

            requirements = analyzer(chatbot, prompt)
            parsed_response = ChatbotUtils.parse_json(requirements)
            output = ChatbotUtils.json_to_md(parsed_response)
            FileUtils.write_to_file(output_file, f"{output}\n", mode='a')

            # adding page break for pandoc
            FileUtils.write_to_file(output_file, "\n\n---\n\n", mode='a')
            # \newpage
            FileUtils.write_to_file(output_file, "\n\n\\newpage\n\n", mode='a')

def main():
    """Entry point for the script."""
    try:
        args = PipelineUtils.get_args()

        logger.info(f"args.create_questionnaire: {args.create_questionnaire}")

        document_types = ['pdf', 'txt', 'md']

        if args.type not in document_types:
            logger.error("The type should be " + " or ".join(document_types))
            raise ValueError("The type should be " + " or ".join(document_types))

        output_file = get_output_file(args.path)

        logger.info(f"Output file: {output_file}")

        if args.remove_duplicates:
            logger.info("Removing duplicates...")
            remove_duplicates(args, output_file)

        elif args.create_questionnaire:

            logger.info("Creating questionnaire...")

            for area, requirement in organize_content(args, output_file, True):
                logger.info("Creating questionnaire for area '%s' and requirement '%s'...", area, requirement)
                create_questionnaire(area, requirement, output_file)

            convert_json_to_md(output_file)
        elif args.repair_md:
            try:
                logger.info("Repairing markdown file...")
                ChatbotUtils.rapair_md_file(args.path, args.output_path)
                output_file = args.output_path
                convert_md_to_docx(output_file)
            except Exception as e:
                logger.error("Error reparing markdown file: %s", e)
                raise e
            return
        elif args.deep_organize:
            logger.info("Deep organizing content...")
            deep_organizer(args, output_file, False)
        else:
            logger.info("Organizing content...")
            organize_content(args, output_file, False)

        logger.info("Converting markdown to docx...")
        convert_md_to_docx(output_file)

    except KeyboardInterrupt:
        logger.info("Exiting the script...")
    except Exception as e:
        logger.error("Error organizing content: %s", e)
        raise e

if __name__ == "__main__":
    main()
