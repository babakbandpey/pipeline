"""
This script reads file's content and organizes it in a structured way.
"""

from typing import Union
import datetime
from pipeline import PipelineUtils, FileUtils, ChatbotUtils

def analyzer(chatbot, prompt: str) -> Union[dict, str]:
    """
    Analyzes a single file and writes the results to the output file.
    :param chatbot: Chatbot object of the classes TextRAG or PdfRAG
    :param prompt: Prompt to be analyzed
    :return: JSON response
    """

    ChatbotUtils.logger().info("prompt %s...", prompt)

    response = chatbot.invoke(
        f"""
        {prompt}
        Format the output as JSON.
        Example: {{"areas_covered": [List of the areas covered by the content]}}
        """
    )

    ChatbotUtils.logger().info("response %s...", response)

    return ChatbotUtils.parse_json(response)


def organize_content(args):
    """
    Main function to organize the content of files.
    :param args: Arguments passed to the script
    """

    files = FileUtils.get_files_from_path(args.path, f".{args.type}")

    for file in files:
        # Create an output file with timestamp .md file and write the response to it
        output_file = (
            f"{file.replace(' ', '-').replace('.pdf', '').replace('.txt', '')}-"
            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        args.collection_name = f"organizer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chatbot = PipelineUtils.create_chatbot(args)

        ChatbotUtils.logger().info("............................................")
        # Get absolute path of the file

        prompt = "Analyze the content and make a list of which areas it covers."
        topics = analyzer(chatbot, prompt)

        for i, area in enumerate(topics['areas_covered']):
            FileUtils.write_to_file(output_file, f"## {i + 1} - {area}\n\n")

            prompt= f"""
            List the very relevant requirements needed to comply with '{area}'.
            If the requirements are repeated, there should be a good reason for mentioning them again.
            """
            requirements = analyzer(chatbot, prompt)
            for key in requirements:
                for z, requirement in enumerate(requirements[key]):
                    output = ChatbotUtils.process_json_response(requirement)
                    if output.startswith(" - "):
                        FileUtils.write_to_file(output_file, f"{output}\n")
                    else:
                        FileUtils.write_to_file(output_file, f"**{i + 1}.{z + 1}:** {output}\n")

        chatbot.delete_collection()
        chatbot.clear_chat_history()

        ChatbotUtils.logger().info("::::::::::::::::::::::::::::::::::::::::::::")


def main():
    """Entry point for the script."""

    args = PipelineUtils.get_args()

    if args.type not in ['pdf', 'txt']:
        raise ValueError("The type should be 'pdf' or 'txt'.")

    try:
        organize_content(args)
    except KeyboardInterrupt:
        ChatbotUtils.logger().info("Exiting the script...")

if __name__ == "__main__":
    main()
