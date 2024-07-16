

import inspect
import os
import logging
from .config import LOGGING_LEVEL

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
        # Get the original message
        message = super().format(record)

        # Apply color based on the log level
        color = self.COLORS.get(record.levelname, self.RESET)
        message = f"{color}{record.levelname}: {message}{self.RESET}"

        return message

# Create a handler
handler = logging.StreamHandler()
# Set the custom formatter
formatter = ColoredFormatter('%(asctime)s - %(filename)s:%(lineno)d - %(message)s')
handler.setFormatter(formatter)

# Set up the root logger
logger = logging.getLogger(get_importing_file_name())
logger.setLevel(LOGGING_LEVEL)
logger.addHandler(handler)
