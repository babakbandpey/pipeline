# README.md

## Introduction
This repository contains a collection of Python scripts designed to facilitate various tasks related to file operations, chatbot interactions, and retrieval-augmented generation (RAG) pipelines. The scripts are organized under the `/app/pipeline` directory and provide functionalities such as loading and processing documents, setting up chatbots, and integrating with external tools like Nmap.

## Detailed Description of Each Script

### 1. `file_utils.py`
The `file_utils.py` file contains a utility class named `FileUtils` that provides various static methods for performing file operations. These methods include retrieving files with a specified extension, writing to files, reading files, prepending content to files, cleaning non-ASCII bytes, and finding non-ASCII bytes in files. The class also includes logging and error handling mechanisms to ensure smooth operation and debugging.

### 2. `json_rag.py`
The `json_rag.py` file implements the `JsonRAG` class, which is designed to handle Retrieval-Augmented Generation (RAG) for JSON documents. This class extends the `Retrieval` class and provides functionalities to load, process, and store JSON documents for efficient retrieval. It includes methods for loading documents from the filesystem, splitting them into chunks, and storing them in a vector store.

### 3. `nmap_scanner.py`
The `nmap_scanner.py` file facilitates the execution and parsing of Nmap scans. The `NmapScanner` class within this file includes methods for running Nmap commands, parsing the output, and retrieving both raw and structured data. The class uses regular expressions to extract relevant information from the Nmap scan results.

### 4. `pdf_rag.py`
The `pdf_rag.py` file is designed to handle the loading, processing, and retrieval of PDF documents. It extends the `Retrieval` class and introduces the `PdfRAG` class, which manages PDF documents by loading them from a specified path, splitting them into smaller chunks, and storing these chunks in a vector store for efficient retrieval.

### 5. `pipeline.py`
The `pipeline.py` file defines a pipeline for integrating the Ollama model with the Langchain library. It includes several classes and functions responsible for different aspects of the pipeline's functionality, such as logging, session management, chat configuration, chat operations, text splitting, and vector store management. The code is designed to create a robust and flexible pipeline for building advanced chatbot applications.

### 6. `pipeline_utils.py`
The `pipeline_utils.py` file contains utility functions and classes that facilitate the operation of a chatbot pipeline. The `PipelineUtils` class provides methods for parsing command-line arguments, printing help messages, creating chatbot instances, retrieving base URLs and API keys, constructing keyword arguments, and handling various chatbot commands.

### 7. `rag_factory.py`
The `rag_factory.py` file implements a factory design pattern to facilitate the creation of various Retrieval-Augmented Generation (RAG) objects based on a specified type. The `RAGFactory` class contains a static method `get_rag_class` that maps type strings to specific RAG implementations, imports the necessary modules, and instantiates the appropriate classes.

### 8. `retrieval.py`
The `retrieval.py` file defines the `Retrieval` class, which sets up and manages a chatbot pipeline that retrieves documents and answers questions based on those documents. The class includes methods for setting up chat prompts, creating processing chains, loading documents, invoking the chatbot, and checking for non-ASCII bytes in files. It also includes robust error handling and logging to ensure smooth operation.

### 9. `web_rag.py`
The `web_rag.py` file contains the implementation of the `WebRAG` class, which creates a pipeline for a chatbot that retrieves documents from a website and answers questions based on those documents. The class is responsible for initializing the pipeline, loading documents from a specified URL, splitting the text data, and setting up a vector store for efficient retrieval.

## Usage
To use the scripts in this repository, follow these steps:
1. Clone the repository to your local machine.
2. Navigate to the `/app/pipeline` directory.
3. Run the desired script using Python. For example:
   ```bash
   python file_utils.py
   ```
4. Follow the instructions provided by the script to perform the desired operations.

## Contributing
We welcome contributions to this project. If you would like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository.
5. Create a pull request to the main repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Authors
- Babak Bandpey <bb@cocode.dk>

## Acknowledgements
We would like to thank the contributors and the open-source community for their valuable input and support in developing this project.
