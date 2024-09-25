'''
This script is used to create podcast content from unorganized text material.
'''

import datetime
import sys
from pipeline import PipelineUtils, FileUtils, logger
from scripts import analyzer, get_output_file

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
        chatbot = PipelineUtils.create_chatbot(args)

        logger.info(f"Processing file: {file}")

        # Identify the main subject
        prompt_main_subject = (
            "Please identify the main subject of the content. "
            "Provide the main subject as a single concise phrase."
        )
        response_main_subject = analyzer(chatbot, prompt_main_subject)
        main_subject = response_main_subject.get('main_subject', 'موضوع اصلی نامشخص')

        content.append(f"% {main_subject}\n\n")

        # Identify sub-subjects
        prompt_sub_subjects = (
            "Based on the content, please identify the key subtopics or sub-subjects "
            "that are discussed. Provide a list of these sub-subjects.\n\n"
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
                f"Please extract all relevant information from the text related to the sub-subject '{sub_subject}'. "
                "Ensure that the extracted text is coherent and repair any incoherence if necessary.\n\n"
                "Provide the extracted and coherent text."
                "Format of the response should be like this:\n"
                "{\n"
                "    'text': 'Extracted text for the sub-subject'\n"
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
                f"{sub_text}\n\n"
                "Provide the narrative text."
                "Format of the response should be like this:\n"
                "{\n"
                "    'narration': 'Narrative text for the sub-subject'\n"
                "}"
            )
            response_narration = analyzer(chatbot, prompt_narration)
            narration_text = response_narration.get('narration', '')

            logger.info("Narration for sub-subject '%s': %s", sub_subject, narration_text)

            if not narration_text:
                logger.error("No narration generated for sub-subject '%s'.", sub_subject)
                sys.exit(1)

            # Translate the text into conversational Persian
            prompt_translation = (
                "Please translate the following text into conversational Persian.\n\n"
                f"{narration_text}\n\n"
                "Provide the translated text."
                "Format of the response should be like this:\n"
                "{\n"
                "    'translation': 'Translated text for the sub-subject'\n"
                "}"
            )
            response_translation = analyzer(chatbot, prompt_translation)
            translated_text = response_translation.get('translation', '')

            logger.info("Translated text for sub-subject '%s': %s", sub_subject, translated_text)

            if not translated_text:
                logger.error("No translation generated for sub-subject '%s'.", sub_subject)
                sys.exit(1)

            content.append(f"{translated_text}\n\n")

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
        podcastit(args, output_file)
    except KeyboardInterrupt:
        logger.info("Exiting the script...")
    except Exception as e:
        logger.error("Error organizing content: %s", e)
        raise e

if __name__ == "__main__":
    main()
