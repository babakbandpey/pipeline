from pipeline.pipeline import Pipeline
from pipeline.pipeline import ChatPromptTemplate, MessagesPlaceholder

# CHATBOT PIPELINE
class ChatbotPipeline(Pipeline):
    """_summary_
    Pipeline for a chatbot
    """

    @staticmethod
    def setup_chat_prompt():
        """
        Sets up the chat prompt for the chatbot.
        returns: The initialized ChatPromptTemplate object.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant.
                    Answer all questions to the best of your ability. """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        return prompt
