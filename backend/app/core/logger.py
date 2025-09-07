import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logger(filename="logs/app.log"):
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)8s - %(message)s (%(filename)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    file_handler = TimedRotatingFileHandler(
        filename=f"{filename}", when="midnight", backupCount=7
    )
    file_formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)8s - %(message)s (%(filename)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger()
