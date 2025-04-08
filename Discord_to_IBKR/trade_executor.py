# trade_executor.py
from ib_insync import *
from datetime import datetime
from constants import IB_HOST, IB_PORT, IB_CLIENT_ID
from utils.queue_manager import get_from_queue
from utils.logging_utils import log_message
from utils.state_manager import set_ibkr_connection_status
from trade_functions import *
import asyncio

def get_nearest_future_contract(ib, symbol):
    """
    Fetch the nearest expiry future contract for the given symbol.
    """
    # Define a generic future contract
    contract = Future(symbol=symbol)
    
    # Fetch contract details
    contracts = ib.reqContractDetails(contract)
    
    if not contracts:
        raise ValueError(f"No contracts found for symbol: {symbol}")
    
    # Find the contract with the nearest expiry
    nearest_contract = min(
        contracts,
        key=lambda x: datetime.strptime(x.contract.lastTradeDateOrContractMonth, "%Y%m%d")
    )
    return nearest_contract.contract

def execute_trade(ib, product, action, symbol, timestamp):
    """
    Execute a trade.
    """
    
    try:
        log_message(f"Executing {action} order for {symbol} at {timestamp}")
        
        # Adjust the symbol for the future contract to MES as this is the micro future for S&P 500
        if symbol == "ES1":
            symbol = "MES"
        
        # Fetch the nearest future contract
        contract = get_nearest_future_contract(ib, symbol)
        
        # Create and place the order
        if action == "buy":
            order = MarketOrder('BUY', 1)
        elif action == "sell":
            order = MarketOrder('SELL', 1)
        else:
            raise ValueError(f"Invalid action: {action}")
        
        log_message(f"Placing {action} order for {symbol} at {timestamp}")
        trade = ib.placeOrder(contract, order)
        # Log the trade details and send the email confirmation
        send_trade_email_confirmation(trade, action, symbol, timestamp)
        log_message(f"Order placed: {trade}")
    except Exception as e:
        log_message(f"Error executing trade: {e}", level="ERROR")
        send_trade_email_confirmation(None, action, symbol, timestamp, error=e)
        set_ibkr_connection_status(False)  # Update IBKR connection status on error

def start_trading_executor():
    """
    Continuously check the queue for new trading commands and execute them.
    """
    # Connect to IB
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, IB_CLIENT_ID)
    set_ibkr_connection_status(True)  # Update IBKR connection status
    
    while True:
        data = get_from_queue()
        if data:
            execute_trade(ib, **data)  # Pass all data, including timestamp