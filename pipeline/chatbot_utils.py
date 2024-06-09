""" This module contains utility functions for the chatbot classes. """
import json
import logging
import re
import inspect
import os
from logging import Logger
from typing import Union


def get_importing_file_name():
    """ Get the name of the file that imports this module. """
    stack = inspect.stack()
    # stack[1] is the caller of the current function
    # stack[2] is the caller of the caller of the current function
    frame = stack[2]
    module = inspect.getmodule(frame[0])
    if module:
        return os.path.basename(module.__file__)
    return None


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(get_importing_file_name())

class ChatbotUtils:
    """Utility class for the chatbot."""
    @staticmethod
    def clean_and_parse_json(text) -> Union[dict, None]:
        """
        Cleans and parses poorly formed JSON text to a dictionary.
        Parameters:
        - text: A string with poorly formed JSON.
        Returns:
        - A dictionary representation of the JSON text or None if parsing fails.
        """
        try:
            text = text.replace("'", '"')
            def replace_inner_quotes(part):
                part = part.strip()
                if part.startswith('"') and part.endswith('"'):
                    part = part[1:-1]
                    part = part.replace('"', "'")
                    part = f'"{part}"'
                return part
            parts = text.split(":")
            for index, part in enumerate(parts):
                if "," in part:
                    sub_parts = part.split(",")
                    sub_parts = [replace_inner_quotes(sub_part) for sub_part in sub_parts]
                    parts[index] = ",".join(sub_parts)
                else:
                    parts[index] = replace_inner_quotes(part)
            text = ":".join(parts)
            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.error("Line: %s", text)
            logging.error("JSONDecodeError: %s", e)
            return None


    @staticmethod
    def parse_json(response) -> Union[dict, str]:
        """
        Parse the JSON response and return the JSON object.
        :param response: The response.
        :return: The JSON object.
        """
        try:
            response = re.sub(r'```json|```', '', response)
            response_json = json.loads(response)
            return response_json
        except json.JSONDecodeError:
            # logging.error("Error: The response is not a valid JSON.")
            return response


    @staticmethod
    def process_json_response(response) -> str:
        """
        Process the JSON response and return a markdown list.
        :param response: The response.
        :return: The markdown list.
        """
        try:
            response_json = ChatbotUtils.parse_json(response)

            if isinstance(response_json, str):
                return response_json

            # Create a markdown list from the JSON data
            markdown_list = ""
            for key, items in response_json.items():
                markdown_list += f"**{key}**\n"
                for item in items:
                    markdown_list += f"\t- {item}\n"

            return markdown_list

        except json.JSONDecodeError:
            # If the response is not JSON, return the original text
            return response
        except ValueError:
            # If the response is not JSON, return the original text
            return response


    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validates the provided URL.
        params: url: The URL to validate.
        returns: True if the URL is valid, False otherwise.
        """
        if not url:
            return False
        # Simple regex for URL validation
        regex = re.compile(
            r'^(?:http|https)://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    @staticmethod
    def logger() -> Logger:
        """
        Set up logging
        :return: logging
        """
        return logger
