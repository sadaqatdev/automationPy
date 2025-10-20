# utils.py
from loguru import logger
import os

_LOGGER_INITIALIZED = False

def setup_logging():
    """Safe logging for Streamlit Cloud – no Streamlit internals or multiprocessing."""
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED:
        return

    # make sure a local log file exists
    log_path = "app.log"
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)

    # remove default handlers and log to console + file
    logger.remove()
    logger.add(log_path, rotation="5 MB", level="INFO", enqueue=False)
    logger.add(lambda m: print(m, end=""), level="INFO")  # show logs in Cloud console
    logger.info("Logger initialized.")

    _LOGGER_INITIALIZED = True
