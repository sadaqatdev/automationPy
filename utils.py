# utils.py
from loguru import logger
import os
import streamlit as st

def setup_logging():
    # put logs under the writable temp dir Streamlit provides
    log_dir = os.path.join(st.runtime.scriptrunner.script_run_context.get_script_run_ctx().session_data_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    # remove default handler first
    logger.remove()

    # 🔧  safest option — synchronous write only
    logger.add(log_path, rotation="5 MB", level="INFO", enqueue=False)
    logger.add(lambda m: print(m, end=""), level="INFO")  # also echo to console
    logger.info("Logger initialized.")
