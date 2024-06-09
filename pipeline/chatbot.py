"""
file: pipeline/chatbot.py
class: Chatbot
Chatbot pipeline module.
"""
import logging
from .pipeline import Pipeline

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING for production
logger = logging.getLogger(__name__)

# CHATBOT PIPELINE
class Chatbot(Pipeline):
    """
    Pipeline for a chatbot
    """

    def invoke(self, prompt):
        """
        Invoke the chatbot pipeline
        params:
            prompt (str): The prompt to send to the chatbot.
        returns:
            str: The response from the chatbot.
        raises:
            ValueError: If the prompt is invalid.
            AttributeError: If the response object does not have the expected attribute.
        """
        # Validate and sanitize the prompt
        if not isinstance(prompt, str) or not prompt.strip():
            self.logger.error("Invalid prompt provided")
            return "Invalid prompt provided. Please provide a non-empty string."

        sanitized_prompt = self.sanitize_input(prompt)

        try:
            response = super().invoke(sanitized_prompt)

            # Ensure response has the expected attribute
            if not hasattr(response, 'content'):
                self.logger.error("Response object does not have 'content' attribute")
                raise AttributeError("Response object does not have 'content' attribute")

            return response.content
        except AttributeError as e:
            self.logger.exception(
                "AttributeError occurred while invoking the chatbot pipeline"
            )
            raise e
        except Exception as e:
            self.logger.exception(
                "An unexpected error occurred while invoking the chatbot pipeline"
            )
            raise e

    def sanitize_input(self, input_str):
        """
        Sanitize the input to remove or escape potentially harmful characters.
        params:
            input_str (str): The input string to sanitize.
        returns:
            str: The sanitized input string.
        """
        # Example sanitization logic (this should be customized based on actual requirements)
        sanitized_str = input_str.replace("<", "&lt;").replace(">", "&gt;")
        return sanitized_str
