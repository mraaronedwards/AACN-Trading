import requests
import json
import re
import csv
from datetime import datetime, timezone

def retrieve_trading_messages(channel_id, year_to_date=True):
    # Store your token securely, not in the code
    headers = {
        'authorization': 'OTI2MTg0MTY0NDk0MDIwNjU5.GW0f0C.OMg1h2PQKQzORD1zWUGDmGcT4ns_9Gca5fS7Uo'
    }
    
    # Get current year's start date (as UTC timezone-aware)
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1, tzinfo=timezone.utc)
    
    all_messages = []
    # First request - get most recent messages
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=100'
    
    while True:
        r = requests.get(url, headers=headers)
        
        if r.status_code != 200:
            print(f"Error: {r.status_code} - {r.text}")
            break
            
        messages = json.loads(r.text)
        
        # If no messages returned, break
        if not messages:
            break
            
        all_messages.extend(messages)
        
        # Check if we've reached messages from before this year
        if year_to_date:
            # Parse ISO timestamp and ensure it's timezone-aware
            oldest_message_time = datetime.fromisoformat(messages[-1]['timestamp'].replace('Z', '+00:00'))
            if oldest_message_time < start_of_year:
                # Filter out messages from before this year
                all_messages = [m for m in all_messages if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) >= start_of_year]
                break
        
        # Get ID of oldest message for pagination
        last_message_id = messages[-1]['id']
        
        # Update URL with before parameter for pagination
        url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=100&before={last_message_id}'
        
        print(f"Retrieved {len(all_messages)} messages so far...")
        
        # Optional: Add a small delay to avoid rate limiting
        # import time
        # time.sleep(0.5)
    
    # Process messages and extract trading data
    # Pattern: "@everyone Lodson 5m ES_F V1 order sell ES1! filled at 5954.00 new position is -1 ES1!"
    pattern = r"@everyone Lodson \w+ ES_F V1 order (buy|sell) ES1! filled at (\d+\.\d+) new position is ([-\d]+) ES1!"
    
    trading_data = []
    
    for message in all_messages:
        content = message['content']
        timestamp = message['timestamp']
        
        # Check if message matches our pattern
        match = re.search(pattern, content)
        if match:
            order_type, fill_price, position = match.groups()
            
            # Format timestamp for better readability
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert position to integer
            position = int(position)
            
            # Convert fill_price to float
            fill_price = float(fill_price)
            
            # Add to our trading data
            trading_data.append({
                'timestamp': formatted_timestamp,
                'order_type': order_type,
                'fill_price': fill_price,
                'position': position
            })
            
            print(f"Found trade: {order_type} at {fill_price} on {formatted_timestamp}, position: {position}")
    
    # Save to CSV
    if trading_data:
        save_to_csv(trading_data)
        
    print(f"Total trading messages found: {len(trading_data)}")
    return trading_data

def save_to_csv(trading_data):
    filename = "Bender_YTD_messages.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'order_type', 'fill_price', 'position']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for data in trading_data:
            writer.writerow(data)
            
    print(f"Trading data saved to {filename}")

# Call the function with your channel ID
trading_data = retrieve_trading_messages('1247171895648845874')