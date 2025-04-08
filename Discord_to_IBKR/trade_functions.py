from ib_insync import *
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from constants import *
from utils.logging_utils import log_message

#find nearest future contract for a symbol
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

## Send email confirmation for the executed trade
def send_trade_email_confirmation(trade, action, symbol, timestamp, error=None):
    """
    Send an email confirmation for the executed trade.
    """
    try:
        # Create the email message
        subject = "Trade Execution Confirmation - TEST"
        body = f"""
        Trade Details:
        - Action: {action}
        - Symbol: {symbol}
        - Timestamp: {timestamp}
        """
        
        if trade:
            body += f"""
            - Order ID: {trade.order.orderId}
            - Status: {trade.orderStatus.status}
            - Filled Quantity: {trade.orderStatus.filled}
            - Average Price: {trade.orderStatus.avgFillPrice}
            """
        elif error:
            subject = "Trade Execution Failure - TEST"
            body += f"""
            - Error: {error}
            """
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        
        log_message("Email confirmation sent successfully.")
    except Exception as e:
        log_message(f"Error sending email confirmation: {e}", level="ERROR")


