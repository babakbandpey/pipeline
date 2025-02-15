"""
This script scans the codebase and generates README.md files for the specified paths.
"""

import os
import json
import datetime
import secrets
from pipeline import PipelineUtils, FileUtils, logger

def analyze_files_in_path(path, args):
    """
    Analyze files in the specified path and append results to the analysis list.
    params: path: The path to the directory containing the files to analyze.
    params: args: The arguments for the chatbot.
    return: analysis: The list of analysis results for the files in the specified path.
    """

    analysis = []

    for root, dirs, files in os.walk(path):
        if root != path:
            continue  # Skip subdirectories
        dirs[:] = []  # Prevent descending into subdirectories

        files = [f for f in files if not f.startswith('.')]

        for file in files:
            analysis_result = {}
            file_path = os.path.join(root, file)

            if file_path.endswith('.md'):
                continue

            args.path = os.path.abspath(file_path)
            logger.info(args.path)

            if file_path.endswith('.py'):
                args.collection_name = secrets.token_hex(16)
                chatbot = PipelineUtils.create_chatbot(args)
                logger.info("Analyzing %s...", file)
                analysis_result['file'] = args.path

                try:
                    response = chatbot.invoke(
                        f"Write a detailed description of what code in python file: {args.path} is used for, which could be used in creating a detailed flow of the code. " +
                        "Do not write the code itself, but describe what code does and refer to functions and classes that are used in code."
                        "Add how the script is executed if there is a main function which is used to run the script."
                    )
                    analysis_result['description'] = response
                    logger.info(response)
                except ValueError as e:
                    logger.error(e)
                    analysis_result['description'] = "No description available."

                chatbot.delete_collection()
                chatbot.clear_chat_history()

                analysis.append(analysis_result)

    return analysis

def generate_readme_from_analysis(path, analysis, args):
    """
    Append analysis to the README.md for the specified path.
    params: path: The path to the directory containing the README.md file.
    params: analysis: The analysis results to append to the README.md.
    params: args: The arguments for the chatbot.
    """

    readme_path = os.path.join(path, "README.md")
    FileUtils.write_to_file(readme_path, "", mode='w')

    for item in analysis:
        FileUtils.write_to_file(
            readme_path,
            f"## {item['file']}\n\n{item['description']}",
            mode='a'
        )

    # Dump the analysis to a JSON file and update args.path
    analysis_json = json.dumps(analysis, indent=4)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = os.path.join('/app/history', f'analysis_temp_{timestamp}.json')
    FileUtils.write_to_file(analysis_file, analysis_json)
    args.path = analysis_file

    # Load the current README.md content if exists
    args.collection_name = secrets.token_hex(16)
    chatbot = PipelineUtils.create_chatbot(args)

    prompt = (
        f"Analyze the provided JSON file which contains descriptions of Python files in the specified path '{path}'. "
        "Write an introduction to the analysis and summarize the key points from the JSON file."
    )

    response = chatbot.invoke(prompt)
    chatbot.delete_collection()
    chatbot.clear_chat_history()

    FileUtils.prepend_to_file(readme_path, response)

def main():
    """Main function to scan the codebase and generate README.md files for given paths."""
    paths = [
        # '/app/',
        '/app/nmap_project',
        # '/app/pipeline',
        # '/app/scripts',
        # Add other paths as needed
    ]

    args = PipelineUtils.get_args()
    args.model = 'gpt-4o'
    args.type = "py"

    # Analyze files in each path and collect the analysis
    for path in paths:
        analysis = analyze_files_in_path(path, args)
        generate_readme_from_analysis(path, analysis, args)

if __name__ == "__main__":
    main()
