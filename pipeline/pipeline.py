"""
file: pipeline/pipeline.py
class: Pipeline
Author: Babak Bandpey
This class defines a pipeline for integrating Ollama with the Langchain library.
This class is in its early stages and will be updated as the project progresses.
Git Repo: https://github.com/babakbandpey/pipeline
"""

import uuid
import logging
from typing import Union
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from openai import APIConnectionError
from .logger import logger


class PipelineConfig:
    """ Configuration for the pipeline. """
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self.session_id = None
        self.logger = logger
        self.generate_session_id()


    def __getattr__(self, name):
        """
        Get attribute by name
        params: name: The name of the attribute.
        returns: The attribute value if it exists, None otherwise.
        """
        if name in self._kwargs:
            return self._kwargs.get(name)

        self.logger.warning(
            "'%s' object has no attribute '%s' set",
            self.__class__.__name__,
            name
        )

        return None


    def generate_session_id(self):
        """
        Generates a unique session ID.
        """
        self.session_id = str(uuid.uuid4())


class PipelineSetup(PipelineConfig):
    """ Configuration for the chatbot. """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat = None
        self.chat_history = ChatMessageHistory()
        self.chat_prompt = None
        self.chain_with_message_history = None
        self.vector_store = None

        self.setup_chat()
        self.setup_chat_prompt(self.system_prompt_template, self.output_type)


    def setup_chat_prompt(self, system_prompt_template: str = None, output_type: str = None):
        """
        Sets up the chat prompt for the chatbot.
        params: system_template: The system template to use.
        returns: The initialized ChatPromptTemplate object.
        """
        if system_prompt_template is None:
            system_prompt_template = """You are a helpful assistant.
            Answer all questions to the best of your ability."""
        elif not isinstance(system_prompt_template, str):
            raise ValueError("system_template must be a string")

        if output_type:
            system_prompt_template += f' Retun the response as {output_type}.'

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_template),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )

        self.chat_prompt = prompt


    def setup_chain(self) :
        """
        Gets the chat chain for the chatbot.
        returns: The chat chain for the chatbot.
        """
        return self.chat_prompt | self.chat


    def setup_chain_with_message_history(self):
        """
        Sets up a chain with message history.

        Returns:
            RunnableWithMessageHistory: A runnable object with message history.
        """
        if not self.chat or not self.chat_prompt:
            raise ValueError(
                """Chat and chat prompt must be initialized
                before setting up the chain with message history."""
            )
        self.chain_with_message_history = RunnableWithMessageHistory(
            runnable=self.setup_chain(),
            get_session_history=lambda session_history: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )


    def setup_vector_store(self, all_chunks):
        """
        Sets up the vector store with the specified chunks.
        params: all_chunks: The chunks to set up the vector store with.
        returns: The initialized vector store.
        """
        model_name = "all-MiniLM-L6-v2.gguf2.f16.gguf"
        gpt4all_kwargs = {'allow_download': 'True'}

        embeding = GPT4AllEmbeddings(
            model_name = model_name,
            gpt4all_kwargs = gpt4all_kwargs
        )

        if self.collection_name:
            self.vector_store = Chroma.from_documents(
                documents=all_chunks,
                embedding=embeding,
                collection_name=self.collection_name
            )
        else:
            self.vector_store = Chroma.from_documents(
                documents=all_chunks,
                embedding=embeding
            )


    def setup_chat(self):
        """
        Sets up the Ollama object with the specified base URL and model.
        params: base_url: The base URL of the Ollama server.
        params: model: The name of the model to use.
        returns: The initialized Ollama object.
        """
        try:
            if self.openai_api_key:
                # OpenAI
                self.chat = ChatOpenAI(
                    base_url=self.base_url,
                    temperature=0,
                    api_key=self.openai_api_key,
                    model=self.model
                )
            elif not self.model and self.base_url:
                # LM Studio
                self.chat = ChatOpenAI(
                    base_url=self.base_url,
                    temperature=0,
                    api_key=self.openai_api_key if self.openai_api_key else "not-needed"
                )
            else:
                # Ollama
                self.chat = Ollama(
                    base_url=self.base_url,
                    model=self.model
                )

        except APIConnectionError as e:
            self.logger.error("API Connection Error: %s", e)
            raise e
        except Exception as e:
            self.logger.error("Unknown exception occurred: %s", e)
            raise e


class Pipeline(PipelineSetup):
    """
    Represents a pipeline for the chatbot.
    """

    def delete_collection(self):
        """
        Deletes the vector store.
        """
        if self.vector_store:
            self.vector_store.delete_collection()
        else:
            self.logger.warning("Vector store is not initialized")


    def add_texts_to_vector_store(self, all_chunks) -> None:
        """
        Adds the specified text to the vector store.
        params: all_chunks: The text to add to the vector store.
        """
        if not self.vector_store:
            self.setup_vector_store(all_chunks)
        else:
            self.vector_store.add_texts(all_chunks)


    def invoke(self, prompt):
        """
        Invokes the chatbot with the specified query.
        params: prompt: The prompt to use.
        """

        if not self.chain_with_message_history:
            self.setup_chain_with_message_history()

        try:
            response = self.chain_with_message_history.invoke(
                {"input": prompt},
                {"configurable": {"session_id": self.session_id}},
            )
        except Exception as e:
            self.logger.error("Error invoking the chatbot: %s", e)
            raise e

        return response


    def clear_chat_history(self):
        """
        Clears the chat history.
        """
        if self.chat_history:
            self.chat_history.clear()
        else:
            self.logger.warning("Chat history is not initialized")


    def modify_chat_history(self, num_messages: int) -> bool:
        """
        Deletes the chat history.
        params: num_messages: The number of messages to keep.
            If set to 0, all messages will be deleted.
            If number is positive deleting from the start of the list.
            If number is negative deleting from the end of the list.
        returns: True if the chat history is modified, False otherwise.
        """
        if num_messages is None:
            self.logger.warning("Chat history is not initialized")
            return False

        messages = self.chat_history.messages
        len_messages = len(messages)

        if num_messages > len_messages:
            return False

        if num_messages == 0:
            self.clear_chat_history()
        elif num_messages > 0:
            self.chat_history.clear()
            for i in range(num_messages, len_messages):
                self.chat_history.add_message(messages[i])
        elif num_messages < 0:
            self.chat_history.clear()
            for i in range(len_messages + num_messages):
                self.chat_history.add_message(messages[i])

        return True


    def summarize_messages(self) -> bool:
        """
        Summarizes the chat history and deletes the messages.
        returns: True if the chat history is summarized, False otherwise.
        """
        if not self.chat_history:
            self.logger.warning("Chat history is not initialized")
            return False

        stored_messages = self.chat_history.messages
        if len(stored_messages) == 0:
            return False

        summarization_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    "Distill the above chat messages into a single summary message.\
                     Include as many specific details as you can."
                )
            ]
        )
        summarization_chain = summarization_prompt | self.chat

        summary_message = summarization_chain.invoke({"chat_history": stored_messages})

        self.chat_history.clear()
        self.chat_history.add_message(summary_message)

        return True


    @staticmethod
    def recursive_character_text_splitter(
        chunk_size=500,
        chunk_overlap=0
        ) -> RecursiveCharacterTextSplitter:
        """
        Splits the data into chunks using the specified chunk size and overlap.
        params: chunk_size: The size of the chunks.
        params: chunk_overlap: The overlap between the chunks.
        returns: The split data.
        """

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter


    @staticmethod
    def split_data(document_splitter: Union[RecursiveCharacterTextSplitter], data: list) -> list:
        """
        Splits the data into chunks using the specified text splitter.
        params: document_splitter: The text splitter object to split the data with.
        params: data: The data to split.
        returns: The split data.
        """
        if not document_splitter:
            raise ValueError("document_splitter is required")
        if not data:
            raise ValueError("data is required")

        return document_splitter.split_documents(data)


    def sanitize_input(self, input_str) -> str:
        """
        Sanitizes user input to prevent injection attacks.
        params: input_str: The input text to sanitize.
        returns: The sanitized input text.
        """
        # Implement input sanitization logic here
        return input_str
