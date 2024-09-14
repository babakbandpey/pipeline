# Chatbot and Web Retrieval Pipeline

### Latest Updates

- Importing the classes should happen from pipeline inside the project directory
- Outside of the project directory the imports can happen by importing from the pipeline package

- The `OPENAI_API_KEY` should be declared in the `.env` file
- The `OPENAI_API_KEY` should be imported from the `pipeline` package


## Overview

This repository contains the implementation of several classes designed to integrate with the Langchain library to create sophisticated chatbots and retrieval systems that handle real-time data retrieval, conversation management, and dynamic response generation.

### Key Classes

- `Chatbot`: Facilitates general chatbot functionalities.
- `WebRAG`: Focuses on retrieving and processing content from specified URLs to answer queries.
- `PythonRAG`: Handles retrieval-augmented generation (RAG) specific to Python code.
- `TextRAG`: Manages RAG for general text-based content.
- `PdfRAG`: Manages RAG for general PDF-based content.

## Features

- **Modular Design**: Leverages inheritance to build specialized pipelines for different use cases.
- **Dynamic Content Retrieval**: Fetches and processes content dynamically from specified web sources.
- **Context-Aware Conversations**: Maintains conversation history for context-aware responses.
- **Scalable and Extensible**: Easily extendable for additional functionalities such as custom data processing or integration with other services.
- **Custom RAG Pipelines**: Includes Python and text-specific retrieval-augmented generation functionalities.

## Prerequisites

- Python 3.11+
- Dependencies from Langchain library
- Ollama + llama3
- Or OpenAI
- OR LM Studio

## Installation

Clone this repository:

```bash
git clone https://github.com/babakbandpey/pipeline.git
cd pipeline
```

Create a virtual environment:

```bash
python -m venv env
```

Activate the virtual environment:

```bash
# On Windows
env\Scripts\activate

# On Unix or MacOS
source env/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

Install the package in editable mode:

```bash
pip install -e .
```

## Usage

### General Chatbot Pipeline

If you have an OpenAI API key, save it in the `.env` file as `OPENAI_API_KEY`. Otherwise, you can use Ollama and llama3 for the chatbot pipeline.

Initialize and run the `Chatbot` pipeline with the specified `BASE_URL`, `MODEL`, and `OPENAI_API_KEY`:

```python
from pipeline import OPENAI_API_KEY
from pipeline import Chatbot
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"

chatbot = Chatbot(BASE_URL, MODEL, OPENAI_API_KEY)
print(chatbot.invoke("Hello! How are you?"))
```

Or with Ollama:

```python
chatbot = Chatbot(base_url="http://localhost:11434", model="llama3")
print(chatbot.invoke("Hello! How are you?"))
```

### Web Retrieval Pipeline

Initialize and run the `WebRAG`:

```python
from pipeline import OPENAI_API_KEY
from pipeline import WebRAG
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"
chatbot = WebRAG(
     base_url=BASE_URL,
     model=MODEL,
     openai_api_key=OPENAI_API_KEY,
    url=url,
)
print(chatbot.invoke("What is the content of the page about?"))
```

### Python RAG Pipeline

Initialize and run the `PythonRAG` pipeline:

```python
from pipeline import OPENAI_API_KEY
from pipeline import PythonRAG
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"

chatbot = PythonRAG(
        base_url=BASE_URL,
        model=MODEL,
        openai_api_key=OPENAI_API_KEY,
        path='/path/to/python/file.py', # or a folder. Be careful with the size of the folder
        exclude=[
            '**/env/**',
            '**/venv/**',
            '**/node_modules/**',
            '**/dist/**',
            '**/build/**',
            '**/target/**',
            '**/.git/**',
            '**/.idea/**',
            '**/.vscode/**',
            '**/__pycache__/**',
            '**/.pytest_cache/**',
            '**/.mypy_cache/**',
            '**/.tox/**',
            '**/.cache/**',
            '**/.github/**',
            '**/.gitlab/**',
        ]
    )
print(chatbot.invoke("What is the function of the python file?"))
```

### Text RAG Pipeline

Initialize and run the `TextRAG` pipeline:

```python
from pipeline import OPENAI_API_KEY
from pipeline import TextRAG
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"

chatbot = TextRAG(
        base_url=BASE_URL,
        model=MODEL,
        openai_api_key=OPENAI_API_KEY,
        path='/path/to/text/file.txt' # or a folder. Be careful with the size of the folder
    )
print(chatbot.invoke("Summarize the text file."))
```

### PDF RAG Pipeline

Initialize and run the `PdfRAG` pipeline:

```python
from pipeline import OPENAI_API_KEY
from pipeline import PdfRAG
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"

chatbot = PdfRAG(
        base_url=BASE_URL,
        model=MODEL,
        openai_api_key=OPENAI_API_KEY,
        path='/path/to/pdf/file.pdf' # or a folder. Be careful with the size of the folder
    )

print(chatbot.invoke("Summarize the PDF file."))

### Running the Script

You can run the `run.py` script with different configurations as follows:

- To run the general chatbot:
  ```bash
  python ./scripts/run.py --type Chat
```

- To run the WebRAG pipeline:

  ```bash
  python ./scripts/run.py --type web --url https://example.com
  ```
- To run the TextRAG pipeline:

  ```bash
  python ./scripts/run.py --type=text --path /path/to/text/file.txt
  ```
- To run the PythonRAG pipeline with a local path:

  ```bash
  python ./scripts/run.py --type python --path /path/to/python/file.py
  ```
- To run the PythonRAG pipeline with a git URL:

  ```bash
  python ./scripts/run.py --type python --git https://github.com/example/repo.git
  ```
- To run the PdfRAG pipeline:

  ```bash
  python ./scripts/run.py --type pdf --path /path/to/pdf/file.pdf
  ```

### Showing Examples

To see example commands, use the `--example` flag:

```bash
python run.py --example
```

### Commands and Interaction

#### Chatbot Commands

- **/exit**: Exit the conversation.
- **/reset**: Start a new conversation.
- **/history**: Review the conversation's history.
- **/delete**: Delete a number of message from the start or the end of the conversation.
- **/summarize**: Summarize and reset the conversation history.
- **/save**: Save the conversation history to a file under the history folder.
- **/help**: Display the list of available commands.

#### Example Session

Here's an example of interacting with the chatbot:

```plaintext
Welcome to the chatbot!

Today's date and time: 2023-05-08 14:25:34

Enter your message: How are you today?
I'm doing great, thank you for asking! How about you?

Enter your message: /history
Chatbot: [HumanMessage(content='How are you today?'), AIMessage(content='I'm doing great, thank you! How about you?')]

Enter your message: /exit
Goodbye!
```

#### Handling Interruptions

If the chatbot session is interrupted (e.g., by pressing `Ctrl+C`), the system will catch the interruption and safely exit:

```plaintext
^C
Goodbye!
```

## License

This project is licensed under the MIT License - see the LICENSE file for more details.
```markdown
# Project Name

## Introduction
This project is designed to provide various utilities and functionalities, including a chatbot pipeline, environment variable encryption, file encoding checks, and requirements generation. The project is structured into multiple Python scripts, each serving a specific purpose.

## File Descriptions

### /app Directory

- **`setup.py`**: This script is used to package the `pipeline` module for distribution. It includes functions to read requirements and long descriptions from files, and it configures the package metadata and dependencies.
- **`generate_requirements.py`**: This script generates a `requirements.txt` file listing the installed packages in the current environment. It includes options to overwrite existing files and include version numbers.
- **`check_encoding.py`**: This script checks the encoding of specified files. It uses the `chardet` library to detect file encoding and handles various file-related exceptions.
- **`env_encryptor.py`**: This script securely manages environment variables by encrypting and decrypting the values in a `.env` file. It uses cryptographic functions from the `cryptography` library.

## Installation

### /app Directory

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/babakbandpey/pipeline.git
    cd pipeline
    ```

2. **Set Up a Virtual Environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Docker Setup**:
    - **Build the Docker Image**:
        ```sh
        docker build -t pipeline .
        ```
    - **Run the Docker Container**:
        ```sh
        docker run -it --rm pipeline
        ```

### /app/project_nmap Directory

1. **Docker Setup**:
    - **Build the Docker Image**:
        ```sh
        docker build -t project_nmap .
        ```
    - **Run the Docker Container**:
        ```sh
        docker run -it --rm project_nmap
        ```

2. **Running `run.py` within the Docker Container**:
    - Once inside the Docker container shell, navigate to the appropriate directory and execute:
        ```sh
        python run.py
        ```

## Usage

### /app Directory

- **Generating Requirements**:
    ```sh
    python generate_requirements.py --include-versions
    ```

- **Checking File Encoding**:
    ```sh
    python check_encoding.py path/to/file
    ```

- **Encrypting Environment Variables**:
    ```sh
    python env_encryptor.py encrypt path/to/.env
    ```

- **Decrypting Environment Variables**:
    ```sh
    python env_encryptor.py decrypt path/to/.env
    ```

### /app/project_nmap Directory

- **Running `run.py`**:
    - Ensure you are inside the Docker container shell and execute:
        ```sh
        python run.py
        ```

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Authors
- **Babak Bandpey** - [bb@cocode.dk](mailto:bb@cocode.dk)

## Acknowledgements
Special thanks to all contributors and the open-source community for their invaluable support and contributions.
```

This README.md file provides a comprehensive overview of the project, including installation instructions, usage examples, and other relevant information.## Installation
### Clone the Repository
```
git clone https://github.com/babakbandpey/pipeline
cd pipeline
```
### Create and Activate a Virtual Environment
```
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt
```
### Using Docker
Ensure Docker and Docker Compose version 2 are installed, then run:
```
docker-compose up --build
docker-compose up -d
```


