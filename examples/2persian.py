'''
This script is used to translate text from a given txt file using a chatbot.
'''

import datetime
import sys
from pipeline import PipelineUtils, FileUtils, logger
from scripts import analyzer, get_output_file

def translate_text(args, output_file):
    """
    Main function to translate text content from a given txt file.
    :param args: Arguments passed to the script
    """
    # Get all files
    files = FileUtils.get_files(args.path, f".{args.type}")

    for file in files:
        content = []

        # Initialize the chatbot or AI model
        args.collection_name = f"translator_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        chatbot = PipelineUtils.create_chatbot(args)

        logger.info(f"Processing file: {file}")

        # Read the content of the file
        text_content = FileUtils.read_file(file)

        # Split the text content into lines
        lines = text_content.split('\n')

        translated_lines = []

        for line in lines:
            if line.strip() == "":
                translated_lines.append("\n")
                continue

            # Translate each line into conversational Persian
            prompt_translation_line = (
                "Please translate the following text into conversational Persian.\n\n"
                f"'{line}'\n\n"
                "Format of the response should be like this:\n"
                "{\n"
                "    'translation': 'Translated text'\n"
                "}"
            )
            response_translation_line = analyzer(chatbot, prompt_translation_line)
            translated_line = response_translation_line.get('translation', '')

            logger.info("Translated line: %s", translated_line)

            if not translated_line:
                logger.error("No translation generated for line: %s", line)
                sys.exit(1)

            translated_lines.append(translated_line)

        # Join the translated lines with newline characters
        translated_text = "\n".join(translated_lines)

        content.append(translated_text)

        # Write the translated content to the output file
        FileUtils.write_to_file(output_file, "\n\n".join(content), mode='a')

        # Clean up the chatbot collection and history
        chatbot.delete_collection()
        chatbot.clear_chat_history()

        logger.info("Finished processing file: %s", file)


def main():
    """Entry point for the script."""
    try:
        args = PipelineUtils.get_args()
        output_file = get_output_file(args.path)
        translate_text(args, output_file)
    except KeyboardInterrupt:
        logger.info("Exiting the script...")
    except Exception as e:
        logger.error("Error translating content: %s", e)
        raise e

if __name__ == "__main__":
    main()


def podcastit(args, output_file):
    """
    Main function to create podcast content from unorganized text material.
    :param args: Arguments passed to the script
    """
    # Get all files
    files = FileUtils.get_files(args.path, f".{args.type}")

    for file in files:
        content = []

        # Initialize the chatbot or AI model
        args.collection_name = f"deep_organizer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        main_subject = [
            "King Archetype",
            "Warrior Archetype"
        ]

        for subject in main_subject:

            chatbot = PipelineUtils.create_chatbot(args)

            logger.info(f"Processing file: {file}")


            content.append(f"% {subject}\n\n")

            # Identify sub-subjects
            prompt_sub_subjects = (
                f"The content is a talk by 'Robert Moore' on the subject of '{subject}'. "
                "The content is based on 'Jungian psychology and Archetypes'. "
                f"Provide a list of maximum 10 sub-subjects related to the '{subject}'.\n\n"
                "The format of the response should be like this:\n"
                "{\n"
                "    'sub_subjects': [\n"
                "        'Sub-subject 1',\n"
                "        'Sub-subject 2',\n"
                "        'Sub-subject 3',\n"
                "        ...\n"
                "    ]\n"
                "}"
            )
            response_sub_subjects = analyzer(chatbot, prompt_sub_subjects)
            sub_subjects = response_sub_subjects.get('sub_subjects', [])

            logger.info("Sub-subjects identified: %s", sub_subjects)

            if not sub_subjects:
                logger.error("No sub-subjects identified.")
                continue

            for i, sub_subject in enumerate(sub_subjects):
                content.append(f"# {i + 1} - {sub_subject}\n\n")

                # Retrieve text for each sub-subject
                prompt_retrieve_text = (
                    f"Please extract all relevant information from the text related to the sub-subject: '{sub_subject}'. "
                    "Ensure that the extracted text is coherent and detailed. "
                    "Repair any incoherence when necessary. "
                    "Important: Keep any references, examples or citations intact. "
                    f"Important: Add characteristics and attributes of the sub-subject: {sub_subject}. "
                    f"Important: Add names of personalities, places, and events related to the sub-subject: {sub_subject}. It could be fictional or real. "
                    "Do not shorten the text too much.\n\n"
                    "Format of the response should be like this:\n"
                    "{\n"
                    f"    'text': 'Extracted text for the sub-subject: {sub_subject}'\n"
                    "}"
                )
                response_text = analyzer(chatbot, prompt_retrieve_text)

                sub_text = response_text.get('text', '')

                logger.info("Text for sub-subject '%s': %s", sub_subject, sub_text)

                if not sub_text:
                    logger.error("No text retrieved for sub-subject '%s'.", sub_subject)
                    sys.exit(1)

                # Turn the text into narration without losing meaning and sense
                prompt_narration = (
                    "Please rewrite the following text into a narrative form. "
                    "Do not lose any meaning or sense from the original text.\n\n"
                    "Important: Keep any references, examples or citations intact. "
                    "Important: Do not shorten the text. "
                    "Important: Write the text for general public and use your knowledge to describe complex terms.\n\n"
                    f"Text: {sub_text}\n\n"
                    "Format of the response should be like this:\n"
                    "{\n"
                    "    'narration': 'Narrated text'\n"
                    "}"
                )
                response_narration = analyzer(chatbot, prompt_narration)
                narrated_text = response_narration.get('narration', '')

                logger.info("Narration for sub-subject '%s': %s", sub_subject, narrated_text)

                if not narrated_text:
                    logger.error("No narration generated for sub-subject '%s'.", sub_subject)
                    sys.exit(1)

                content.append(f"{narrated_text}\n\n")

        # Write the content to the output file
        FileUtils.write_to_file(output_file, "\n\n".join(content), mode='a')

        # Clean up the chatbot collection and history
        chatbot.delete_collection()
        chatbot.clear_chat_history()

        logger.info("Finished processing file: %s", file)


def main():
    """Entry point for the script."""
    try:
        args = PipelineUtils.get_args()
        output_file = get_output_file(args.path)
        translate_text(args, output_file)
    except KeyboardInterrupt:
        logger.info("Exiting the script...")
    except Exception as e:
        logger.error("Error organizing content: %s", e)
        raise e

if __name__ == "__main__":
    main()
