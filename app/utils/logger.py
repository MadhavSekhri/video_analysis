import logging

# Create logger
logger = logging.getLogger("video-analysis-logger")
logger.setLevel(logging.DEBUG)

# Create file handler
file_handler = logging.FileHandler("app/utils/logs/debug.log")
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Function to log messages
def log_message(message: str, level: str = "INFO"):
    if level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)
