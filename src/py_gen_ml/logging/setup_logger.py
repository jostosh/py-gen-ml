import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Setup a logger with the given name.

    This function sets up a logger with the specified name and returns it.
    The logger is configured to log messages to the console at the INFO level.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
