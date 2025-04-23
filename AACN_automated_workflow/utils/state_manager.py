# utils/state_manager.py
bot_state = "running"  # Can be "running" or "paused"
ibkr_connected = False  # Tracks IBKR connection status

def get_bot_state():
    return bot_state

def set_bot_state(state):
    global bot_state
    bot_state = state

def get_ibkr_connection_status():
    return ibkr_connected

def set_ibkr_connection_status(status):
    global ibkr_connected
    ibkr_connected = status