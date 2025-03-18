# discord_handler.py
import discord
import re
from constants import AUTHORISATION, BOT_USER_ID, TARGET_CHANNEL_ID
from utils.state_manager import get_bot_state
from utils.queue_manager import add_to_queue
from utils.logging_utils import *
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#We take the message here and extract the relevant information
def parse_message(message):
    """
    Parse the message and extract relevant data.
    """
    # Updated pattern to capture only ES_F, action, and ES1!
    pattern = r"@everyone Lodson \d+m (\w+) \w+ order (\w+) (\w+)!"
    match = re.match(pattern, message)
    
    if match:
        product, action, symbol = match.groups()
        return {
            "product": product,
            "action": action,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),  # Add current timestamp
        }
    return None

#Register the function on_message to be called when a message is received
@client.event
async def on_message(message):
    if get_bot_state() == "paused":
        return  # Skip processing if the bot is paused

    #print(f"Message from {message.author.id}: {message.channel.id}") # Delete later
    if message.author.id != BOT_USER_ID or message.channel.id != TARGET_CHANNEL_ID:
        return

    if "Lodson" in message.content:
        parsed_data = parse_message(message.content)
        if parsed_data:
            add_to_queue(parsed_data)  # Add parsed data to the queue

def start_discord_listener():
    """
    Start the Discord listener in a separate thread.
    """
    try:
        log_message("Starting Discord listener...")
        client.run(AUTHORISATION)
    except Exception as e:
        log_message(f"Error in Discord listener: {e}", level="ERROR")
