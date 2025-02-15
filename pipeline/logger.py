import logging
from .config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

logger = logging.getLogger("pipeline")
logger.setLevel(LOG_LEVEL)

# Add file handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)

# Add console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Add formatters
formatter = logging.Formatter(LOG_FORMAT)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add handlers
logger.addHandler(fh)
logger.addHandler(ch)
