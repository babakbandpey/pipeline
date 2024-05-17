"""
file: pipeline/retrieval.py
class: Retrieval
author: Babak Bandpey
This Python code is part of a class named Retrieval.
"""

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from pipeline import Pipeline

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

        This Python code is part of a class method named setup_chain.
        This method is used to set up a chatbot pipeline chain,
        which is a sequence of processing steps for the chatbot.
        The method takes two optional parameters: search_type and search_kwargs.

        The search_type parameter specifies the type of search to use.
        If no search type is provided, the method defaults to using "mmr" as the search type.

        The search_kwargs parameter is a dictionary that contains keyword arguments for the search.
        If no arguments are provided,
        the method defaults to a dictionary with a single key-value pair: {"k": 8}.

        The method then creates a prompt object using the ChatPromptTemplate.
        from_messages method. This method takes a list of messages as input.
        In this case, the list contains three messages.
        The first message is a placeholder for the chat history.
        The second message is the user's input.
        The third message is a prompt for the user to generate a search query based
        on the conversation.

        Next, the method creates a retriever object using the vector_store.as_retriever method.
        This method takes the search_type and search_kwargs as arguments.

        The retriever_chain is then created using the create_history_aware_retriever function.
        This function takes the chat history, the retriever, and the prompt as arguments.

        The doc_combination_chain is created using the create_stuff_documents_chain function.
        This function takes the chat history and the chat prompt as arguments.

        Finally, the method returns a retrieval chain created by the create_retrieval_chain function.
        This function takes the retriever_chain and the doc_combination_chain as arguments.
        The retrieval chain is the final output of the setup_chain method.

        params: search_type: The type of search to use.
        params: search_kwargs: The keyword arguments for the search.

        Returns:
            The retrieval chain for the retrieval chatbot pipeline.
        '''

        if search_type is None:
            search_type = "mmr"

        if search_kwargs is None:
            search_kwargs = {"k": 8}

        prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                (
                    "user",
                    "Given the above conversation, generate a search query to look up to get information relevant to the conversation",
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

    def invoke(self, prompt):
        """
        Invokes the chatbot with the specified query.
        params: prompt: The prompt to use.
        returns: The answer from the chatbot.
        """
        self.chat_history.add_user_message(prompt)
        response = super().invoke(prompt)
        answer = response["answer"]
        self.chat_history.add_ai_message(answer)
        return answer
