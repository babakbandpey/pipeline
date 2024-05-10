# Chatbot and Web Retrieval Pipeline

## Overview

This repository contains the implementation of two main classes: `ChatbotPipeline` and `WebRetrievalPipeline`, both of which extend the base `Pipeline` class. These classes are designed to integrate with the Langchain library to create sophisticated chatbots that can handle real-time data retrieval, conversation management, and dynamic response generation. The `ChatbotPipeline` facilitates general chatbot functionalities, while the `WebRetrievalPipeline` focuses on retrieving and processing content from specified URLs to answer queries.

## Features

- **Modular Design**: Leverages inheritance to build specialized pipelines for different use cases.
- **Dynamic Content Retrieval**: The `WebRetrievalPipeline` fetches and processes content dynamically from specified web sources.
- **Context-Aware Conversations**: Both pipelines maintain conversation history to provide context-aware responses.
- **Scalable and Extensible**: Easily extendable for additional functionalities such as custom data processing or integration with other services.

## Prerequisites

- Python 3.6+
- Dependencies from Langchain library
- Ollama
- llama3

## Installation

Clone this repository:

```bash
git clone https://github.com/babakbandpey/pipeline.git
cd pipeline
```


---

## Installation and Usage Instructions for llama3

For detailed instructions on installing Ollama and running the `llama3` model, please visit the following site:

[Ollama Llama3 Library Instructions](https://ollama.com/library/llama3)

This link provides comprehensive guidance on setup, configuration, and operation of the `llama3` model within the Ollama framework.

---


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

Initialize and run the `ChatbotPipeline`:

```python
from libs.pipeline import ChatbotPipeline

pipeline = ChatbotPipeline(base_url="http://localhost:11434", model="llama3")
response = pipeline.invoke("Your question here")
print(response)
```

### Web Retrieval Pipeline

Initialize and use the `WebRetrievalPipeline` to fetch and respond based on web content:

```python
from libs.pipeline import WebRetrievalPipeline

pipeline = WebRetrievalPipeline(base_url="http://localhost:11434", model="llama3", url="https://www.example.com/")
response = pipeline.invoke("Your question here")
print(response)
```

### Managing Conversations

- **Reset History**: Clears all conversation history.
- **Fetch History**: Prints out the chat history.

```python
pipeline.clear_chat_in_history()
print(pipeline.chat_history.messages)
```

## Contributing

Contributions are welcome! Please read the contributing guide to learn how you can propose bug fixes and improvements.

## Chatbot Interaction Guide

This section explains how to interact with the chatbot using the command-line interface provided by the `ChatbotPipeline` and `WebRetrievalPipeline`. These pipelines leverage advanced memory management techniques to enhance conversation capabilities, making interactions more contextual and responsive.

### Starting the Chatbot

To start a chat session, run the Python script from the command line. Upon startup, the chatbot will display the current date and time, and it will wait for user input:

```bash
python index.py
```

### Chatbot Commands

During the interaction with the chatbot, you can use several commands to control the session:

- **/exit**: Terminate the chatbot session.

  ```bash
  Enter your message: /exit
  ```
- **/reset**: Clear all chat history in the session. This is useful if you want to start a fresh conversation without previous context influencing the responses.

  ```bash
  Enter your message: /reset
  ```
- **/history**: Display all previous messages in the chat history. This command allows you to review the conversation's context and understand how past interactions influence current responses.

  ```bash
  Enter your message: /history
  ```

### Example Session

Here's an example of what interacting with the chatbot might look like:

```plaintext
Welcome to the chatbot!

Today's date and time: 2023-05-08 14:25:34

Enter your message: How are you today?
I'm doing great, thank you for asking! I'm always happy to be of assistance and help with any questions or tasks you may have. It's a beautiful day to be a helpful assistant, isn't it? How about you, how's your day going so far?

Enter your message: /history
Chatbot: [HumanMessage(content='How are you doing today?'), AIMessage(content="I'm doing great, thank you for asking! I'm always happy to be of assistance and help with any questions or tasks you may have. It's a beautiful day to be a helpful assistant, isn't it? How about you, how's your day going so far?")]

Enter your message: /exit

Goodbye!
```

### Handling Interruptions

If the chatbot session is interrupted (e.g., by pressing `Ctrl+C`), the system will catch the interruption and safely exit:

```plaintext
^C

Goodbye!
```

This setup ensures that your interaction with the chatbot is smooth and user-friendly, supporting both ongoing conversations and administrative commands to manage the chat flow.

---

This guide provides users with clear instructions on how to interact with the chatbot, utilize commands, and handle common scenarios during the chat session. It enhances the usability of your application by detailing the operational aspects and user interactions.

## License

This project is licensed under the MIT License - see the LICENSE file for more details.

---

This `README.md` provides a detailed overview of how to set up and use the pipelines, along with information on how they work. Adjust the repository URL and any specific installation instructions as needed to match your project's requirements.
