# trade_executor.py
from Discord_to_IBKR.constants import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, SMTP_SERVER, SMTP_PORT
import smtplib
from Discord_to_IBKR.utils.queue_manager import get_from_queue
from Discord_to_IBKR.utils.logging_utils import log_message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_confirmation(test , error=None):
    """
    Send an email confirmation for the executed trade.
    """
    try:
        # Create the email message
        subject = "Trade Execution Confirmation - Test Mode"
        body = f"""
        Trade Details:
        - Action: {test}
        - Symbol: {test}
        - Timestamp: {test}
        """
        
        if test:
            body += f"""
            - Order ID: {test}
            - Status: {test}
            - Filled Quantity: {test}
            - Average Price: {test}
            """
        elif error:
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

test = "test"
send_email_confirmation(test)