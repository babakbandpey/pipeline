"""
This script reads file's content and organizes it in a structured way.
"""

import os
import logging
import datetime
from pipeline import Utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """ Main function to organize the content of the file. """

    args = Utils.get_args()


    if args.type not in ['pdf', 'text']:
        raise ValueError("The type should be 'pdf' or 'text'.")

    files = Utils.get_files_from_path(args.path, f".{args.type}")

    for file in files:

        # create an output file with timestamp .md file and write the response to it
        time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        name = file.replace(' ', '-').replace('.pdf', '').replace('.txt', '')
        output_file = f"{name}-{time}.md"

        logging.info("............................................")
        # get absolute path of the file
        args.path = os.path.abspath(file)
        args.collection_name = 'organizer_' + time
        chatbot = Utils.create_chatbot(args)

        logging.info("Analyzing %s...", file)
        Utils.write_to_file(output_file, f"# Analyzing {file}...")


        response = chatbot.invoke(
            "Analyze the content and make a list of which areas it covers. " +
            "Format the output as JSON." +
            """
            Example:
            {
                "areas_covered": [List of the areas covered by the content]
            }
            """
        )

        response = chatbot.invoke(
            "Analyze the following text and identify the main topics or areas it covers. " +
            "Sort these areas by their relevance to each other, ensuring that closely related topics are listed together. " +
            "For example, if multiple areas are about 'passwords,' group them together." +
            """
            Example:
            {
                "areas_covered": [List of the topics or areas covered by the content]
            }
            """
        )

        areas_covered = Utils.parse_json_response(response)

        for i, area in enumerate(areas_covered['areas_covered']):
            response = chatbot.invoke(
                f"List the requirements needed to comply with '{area}'. " +
                "Format the output as JSON." +
                """
                Example:
                {
                    "requirements": [List of the requirements to comply with]
                }
                """
            )

            Utils.write_to_file(output_file, f"## {i + 1} - {area}\n\n")

            requirements = Utils.parse_json_response(response)

            for z, requirement in enumerate(requirements['requirements']):
                Utils.write_to_file(output_file, f"**{i + 1}.{z + 1}:** {requirement}.\n")

        chatbot.delete_collection()
        chatbot.clear_chat_history()
        logging.info("::::::::::::::::::::::::::::::::::::::::::::")

if __name__ == "__main__":
    main()
