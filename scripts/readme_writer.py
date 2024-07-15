import os
import json
import datetime
import secrets
from pipeline import PipelineUtils, FileUtils, logger

def analyze_files_in_path(path, args, analysis):
    """Analyze files in the specified path and append results to the analysis list."""
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
                args.type = 'py'
                args.collection_name = secrets.token_hex(16)
                chatbot = PipelineUtils.create_chatbot(args)
                logger.info("Analyzing %s...", file)
                analysis_result['file'] = args.path

                try:
                    response = chatbot.invoke(
                        f"Write a detailed description of what code in python file: {args.path} is used for, which could be used in creating a detailed flow of the code. " +
                        "Do not write the code itself, but describe what code does and refer to functions and classes that are used in code."
                    )
                    analysis_result['description'] = response
                    print(response)
                except ValueError as e:
                    logger.error(e)
                    analysis_result['description'] = "No description available."

                chatbot.delete_collection()
                chatbot.clear_chat_history()

                analysis.append(analysis_result)

def generate_readme_from_analysis(path, analysis, args):
    """Generate README.md for the specified path based on the analysis."""
    # Load the entire analysis into the chatbot and ask for a coherent description for the specific path
    args.type = "json"
    args.path = analysis
    args.model = "gpt-4o"
    chatbot = PipelineUtils.create_chatbot(args)

    prompt = (
        f"Analyze the provided JSON file which contains descriptions of Python files in the specified path '{path}'. "
        "Generate a README.md file with the following sections:\n"
        "1. Introduction\n"
        "2. Detailes description of each script.\n"
        "4. Usage \n"
        "5. Contributing\n"
        "6. License\n"
        "7. Authors\n"
        "8. Acknowledgements\n"
    )

    response = chatbot.invoke(prompt)

    # Write the response to a README.md file
    readme_path = os.path.join(path, "README.md")
    FileUtils.write_to_file(readme_path, response)

def main():
    """Main function to scan the codebase and generate README.md files for given paths."""
    paths = [
        # '/app/',
        '/app/project_nmap',
        '/app/pipeline',
        '/app/scripts',
        # Add other paths as needed
    ]

    args = PipelineUtils.get_args()
    args.model = 'gpt-4o'
    args.type = "py"
    analysis = []

    # Analyze files in each path and collect the analysis
    for path in paths:
        analyze_files_in_path(path, args, analysis)

    # Convert the analysis to a JSON file and save it
    analysis_json = json.dumps(analysis, indent=4)
    time_stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    history_path = '/app/history'
    os.makedirs(history_path, exist_ok=True)
    analysis_file = f"{history_path}/analysis-{time_stamp}.json"
    FileUtils.write_to_file(analysis_file, analysis_json)

    # Generate README.md for each path based on the collected analysis
    for path in paths:
        generate_readme_from_analysis(path, analysis_file, args)

if __name__ == "__main__":
    main()
