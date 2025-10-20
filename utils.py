# utils.py
from loguru import logger
import os

def setup_logging(log_path="logs/app.log"):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger.add(log_path, rotation="5 MB", level="INFO", enqueue=True)
    logger.info("Logger initialized.")
