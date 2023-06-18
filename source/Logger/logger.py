import logging

def setup_logging(name,filepath):
    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create the console handler and set its log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create the file handler and set its log level
    file_handler = logging.FileHandler(filepath)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter for the log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add the formatter to the handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
