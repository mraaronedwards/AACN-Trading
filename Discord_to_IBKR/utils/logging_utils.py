# utils/logging_utils.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    handler = RotatingFileHandler('trade_bot.log', maxBytes=10000, backupCount=1)
    logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_message(message, level="INFO"):
    if level == "INFO":
        logging.info(message)
    elif level == "ERROR":
        logging.error(message)

def get_logs():
    """
    Fetch the latest logs from the log file.
    """
    with open('trade_bot.log', 'r') as f:
        return f.readlines()