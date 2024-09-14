"""
A module for logging messages with color based on the log level.
"""

import inspect
import os
import logging
from .config import LOGGING_LEVEL

def get_importing_file_name():
    """ Get the name of the file that imports this module. """
    stack = inspect.stack()
    frame = stack[2]
    module = inspect.getmodule(frame[0])
    if module:
        return os.path.basename(module.__file__)
    return None

class ColoredFormatter(logging.Formatter):
    """
    A custom logging formatter that adds color to log messages based on the log level.

    Attributes:
        COLORS (dict): A dictionary mapping log levels to their corresponding color codes.
        RESET (str): The color code to reset the color back to the default.

    Methods:
        format(record): Formats the log record by adding color to the log message based on the log level.
    """

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[1;31m' # Bold Red
    }
    RESET = '\033[0m'  # Reset color

    def format(self, record):
        """
        Formats the log record by adding color to the log message based on the log level.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message with color added.
        """
        message = super().format(record)
        color = self.COLORS.get(record.levelname, self.RESET)
        message = f"{color}{record.levelname}: {message}{self.RESET}"
        return message

def initialize_logger() -> logging.Logger:
    """ Initialize the logger with a custom handler and formatter. """
    handler = logging.StreamHandler()
    formatter = ColoredFormatter('%(asctime)s - %(filename)s:%(lineno)d - %(message)s')
    handler.setFormatter(formatter)

    # Get the name of the importing file
    importing_file_name = get_importing_file_name()

    # Set up the logger
    l = logging.getLogger(importing_file_name)
    l.setLevel(LOGGING_LEVEL)
    l.addHandler(handler)

    return l

# Initialize the logger and expose it as a module-level variable
logger = initialize_logger()
