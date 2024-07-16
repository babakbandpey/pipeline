""" This module contains utility functions for the chatbot classes. """
import json
import re
from typing import Union
from .logger import logger

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
            logger.error("Line: %s", text)
            logger.error("JSONDecodeError: %s", e)
            return None


    @staticmethod
    def extract_commands_json(text):
        """
        Extracts the JSON object that contains 'commands' and 'command' keys from the given text.

        Args:
        text (str): The text containing JSON data.

        Returns:
        dict: The extracted JSON object as a Python dictionary.
        """
        json_pattern = re.compile(r'\{.*?\}', re.DOTALL)

        # Find all matches in the text
        matches = json_pattern.findall(text)
        print(matches)
        print(len(matches))
        # Join matches to form complete JSON objects
        json_candidates = []
        current_json = ""
        for match in matches:
            current_json += match
            try:
                json_data = json.loads(current_json)
                json_candidates.append(json_data)
                current_json = ""
            except json.JSONDecodeError:
                # Continue appending until we get a valid JSON
                continue
        print(json_candidates)
        for json_data in json_candidates:
            # Check if the JSON object contains the specific keys
            if 'commands' in json_data and isinstance(json_data['commands'], list):
                for command in json_data['commands']:
                    if 'command' in command:
                        return json_data

        raise ValueError("No JSON object with the required keys found in the response")


    @staticmethod
    def extract_json(response):
        """
        Extracts and returns the JSON part from the given response string.

        Args:
        response (str): The response string containing JSON data.

        Returns:
        dict: The extracted JSON data as a Python dictionary.
        """
        # Regular expression to find JSON-like content
        json_pattern = re.compile(r'\{(?:[^{}]|(?R))*\}')

        # Search for the JSON part in the response
        match = json_pattern.search(response)

        if match:
            json_str = match.group(0)
            try:
                json_data = json.loads(json_str)
                return json_data
            except json.JSONDecodeError as exc:
                raise ValueError("Extracted data is not valid JSON") from exc
        else:
            raise ValueError("No JSON data found in the response")


    @staticmethod
    def parse_json(response) -> Union[dict, str]:
        """
        Parse the JSON response and return the JSON object.
        :param response: The response.
        :return: The JSON object.
        """
        # if response is dict, return it
        if isinstance(response, dict):
            return response

        try:
            response = re.sub(r'```json|```', '', response)
            response_json = json.loads(response)
            return response_json
        except json.JSONDecodeError:
            # logger.error("Error: The response is not a valid JSON.")
            return response
        except ValueError:
            # logger.error("Error: The response is not a valid JSON.")
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
