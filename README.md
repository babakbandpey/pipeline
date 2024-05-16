Here are the updates based on the functionalities in the provided Python files:

1. **New Features**: Added specific functionalities and changes.
2. **Updated Installation and Usage Instructions**.
3. **Enhanced descriptions for new classes or methods**.

Here's the updated `README.md` content:

---

# Chatbot and Web Retrieval Pipeline

## Overview

This repository contains the implementation of several classes designed to integrate with the Langchain library to create sophisticated chatbots and retrieval systems that handle real-time data retrieval, conversation management, and dynamic response generation.

### Key Classes
- `Chatbot`: Facilitates general chatbot functionalities.
- `WebRAG`: Focuses on retrieving and processing content from specified URLs to answer queries.
- `PythonRAG`: Handles retrieval-augmented generation (RAG) specific to Python code.
- `TextRAG`: Manages RAG for general text-based content.


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
- Or openai
- OR LM Studio

## Installation

Clone this repository:

```bash
git clone https://github.com/babakbandpey/pipeline.git
cd pipeline
```

Create a virtual environment:

```bash
python3 -m venv env
```

Activate the virtual environment:

```bash
source env/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### General Chatbot Pipeline

if you have an OpenAI API key, save it in the .env file as OPENAI_API_KEY. Otherwise, you can use Ollama and llama3 for the chatbot pipeline.


Initialize and run the `Chatbot` pipeline with the specified `BASE_URL`, `MODEL`, and `OPENAI_API_KEY`:

```python
import pipeline
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"
OPENAI_API_KEY = pipeline.OPENAI_API_KEY

chatbot = pipeline.ChatbotPipeline(BASE_URL, MODEL, OPENAI_API_KEY)
print(chatbot.invoke("Hello! How are you?"))
```

Or with Ollama:
```python
chatbot = pipeline.Chatbot(base_url="http://localhost:11434", model="llama3")
print(chatbot.invoke("Hello! How are you?"))
```

### Web Retrieval Pipeline

Initialize and run the `WebRAG`

```python
import pipeline
BASE_URL = "https://api.openai.com/v1/"
MODEL = "gpt-4o"
OPENAI_API_KEY = pipeline.OPENAI_API_KEY
chatbot = pipeline.WebRAG(
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
import pipeline

chatbot = pipeline.PythonRAG(
        base_url=BASE_URL,
        model=MODEL,
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
import pipeline

chatbot = pipeline.TextRAG(
        base_url=BASE_URL,
        model=MODEL,
        openai_api_key=OPENAI_API_KEY,
        path='/path/to/text/file.txt' # or a folder. Be careful with the size of the folder
    )
print(chatbot.invoke("Summarize the text file."))
```

## Commands and Interaction

### Chatbot Commands

- **/exit**: Exit the conversation.
- **/reset**: Start a new conversation.
- **/history**: Review the conversation's history.
- **/delete**: Delete a number of message from the start or the end of the conversation.
- **/summarize**: Summarize and reset the conversation history.
- **/save**: Save the conversation history to a file under the history folder.
- **/help**: Display the list of available commands.


### Example Session

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

### Handling Interruptions

If the chatbot session is interrupted (e.g., by pressing `Ctrl+C`), the system will catch the interruption and safely exit:

```plaintext
^C
Goodbye!
```

## License

This project is licensed under the MIT License - see the LICENSE file for more details.

---

This `README.md` provides a comprehensive overview of how to set up and use the pipelines, along with information on how they work. Adjust the repository URL and any specific installation instructions as needed to match your project's requirements.
