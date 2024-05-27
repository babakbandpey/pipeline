"""
file: pipeline/chatbot.py
class: Chatbot
Chatbot pipeline module.
"""
from .pipeline import Pipeline

# CHATBOT PIPELINE
class Chatbot(Pipeline):
    """
    Pipeline for a chatbot
    """

    def invoke(self, prompt):
        """
        Invoke the chatbot pipeline
        params: prompt: The prompt to send to the chatbot
        returns: The response from the chatbot
        """
        response = super().invoke(prompt)
        return response.content
