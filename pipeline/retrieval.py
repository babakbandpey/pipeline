"""
file: pipeline/retrieval.py
class: Retrieval
author: Babak Bandpey
This Python code is part of a class named Retrieval.
"""

import os
import sys
from abc import abstractmethod
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from .pipeline import Pipeline
from .file_utils import FileUtils

class Retrieval(Pipeline):
    """
    Pipeline for a chatbot that retrieves documents and answers questions
    based on the retrieved documents.
    """
    def setup_chat_prompt(self, system_template=None):
        """
        Sets up the prompt for the chatbot.
        params: system_template: The system template to use.
        """
        if system_template is None:
            system_template = """
            Answer the user's questions based on the below context.
            If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

            <context>
            {context}
            </context>
            """

        if not isinstance(system_template, str):
            self.logger.error("system_template must be a string %s", system_template)
            raise ValueError("system_template must be a string")

        if "{context}" not in system_template:
            system_template = system_template + """

            <context>
            {context}
            </context>
            """

        super().setup_chat_prompt(system_template)


    def setup_chain(self, search_type=None, search_kwargs=None):
        '''
        Set up the chatbot pipeline chain.

        This method creates a chain of processing steps for the chatbot pipeline.

        params: search_type: The type of search to use.
        params: search_kwargs: The keyword arguments for the search.

        Returns:
            The retrieval chain for the retrieval chatbot pipeline.
        '''
        valid_search_types = ["mmr", "similarity", "similarity_score_threshold"]
        if search_type is None:
            search_type = "mmr"
        elif search_type not in valid_search_types:
            raise ValueError(
                f"Invalid search_type: {search_type}."
                f"Must be one of {valid_search_types}."
            )

        if search_kwargs is None:
            search_kwargs = {"k": 50, "fetch_k": 50}
        elif not isinstance(search_kwargs, dict):
            raise ValueError("search_kwargs must be a dictionary")
        elif not all(isinstance(v, int) and v > 0 for v in search_kwargs.values()):
            raise ValueError("All values in search_kwargs must be positive integers")

        prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                (
                    "user",
                    (
                        "Given the above conversation, generate a search query"
                        " to look up to get information relevant to the conversation"
                    )
                ),
            ]
        )

        retriever = self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

        retriever_chain = create_history_aware_retriever(self.chat, retriever, prompt)

        doc_combination_chain = create_stuff_documents_chain(self.chat, self.chat_prompt)
        return create_retrieval_chain(
            retriever_chain,
            doc_combination_chain
        )


    def load_documents(self):
        """Loads Python documents from the filesystem."""
        try:
            self._load_documents()
        except UnicodeDecodeError as e:
            self.logger.error("UnicodeDecodeError occurred: %s", e)
        except ValueError as e:
            self.logger.error("ValueError: %s", e)
            sys.exit(1)
        except FileNotFoundError as e:
            self.logger.error("FileNotFoundError occurred: %s", e)
        except PermissionError as e:
            self.logger.error("PermissionError occurred: %s", e)


    @abstractmethod
    def _load_documents(self):
        """
        Loads documents from the filesystem.
        This method initializes the documents attribute.
        """


    def invoke(self, prompt) -> str:
        """
        Invokes the chatbot with the specified query.
        params: prompt: The prompt to use.
        returns: The answer from the chatbot.
        """
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")

        sanitized_prompt = self.sanitize_input(prompt)
        self.chat_history.add_user_message(sanitized_prompt)

        response = super().invoke(sanitized_prompt)
        answer = response.get("answer", "No answer found")

        self.chat_history.add_ai_message(answer)
        return answer


    def check_for_non_ascii_bytes(self):
        """
        Checks for non-ASCII bytes in a text file or directory.
        If non-ASCII bytes are found, the user is prompted to clean the file.
        """
        def detect_and_clean(file_path):
            self.logger.info("Checking file: %s for non-ASCII bytes...", file_path)
            non_ascii_positions = FileUtils.find_non_ascii_bytes(file_path)
            if non_ascii_positions:
                self.logger.warning("Non-ASCII bytes found in file: %s", file_path)
                self.logger.warning(non_ascii_positions)
                if self.auto_clean:
                    FileUtils.clean_non_ascii_bytes(file_path)
                else:
                    raise ValueError(
                        f"Non-ASCII bytes found in file: {file_path}."
                         "Please clean the file manually."
                    )

        if not os.path.exists(self.path):
            raise ValueError(f"Invalid path: {self.path}. No such file or directory.")
        if os.path.isdir(self.path):
            for file in os.listdir(self.path):
                if file.endswith(".txt"):
                    file_path = os.path.join(self.path, file)
                    detect_and_clean(file_path)
        else:
            detect_and_clean(self.path)
