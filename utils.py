# utils.py
from loguru import logger
import os

def setup_logging():
    logger.remove()  # clear default handlers
    logger.add("app.log", rotation="5 MB", level="INFO", enqueue=False)
    logger.add(lambda msg: print(msg, end=""), level="INFO")  # console output for Streamlit
    logger.info("Logger initialized.")

