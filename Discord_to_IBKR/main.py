# main.py
from discord_handler import start_discord_listener
from trade_executor import start_trading_executor
from utils.logging_utils import setup_logging
from utils.state_manager import set_bot_state
import threading

def setup():
    """
    Initialize the application (logging, state, etc.).
    """
    setup_logging()
    set_bot_state("running")  # Start the bot in running state

if __name__ == "__main__":
    # Step 1: Initialize the application
    setup()

    # Step 2: Start the Discord listener in a separate thread
    discord_thread = threading.Thread(target=start_discord_listener)
    discord_thread.start()
    # Step 3: Start the trading executor 
    start_trading_executor()
