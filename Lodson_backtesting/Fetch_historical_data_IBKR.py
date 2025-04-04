from ib_insync import *
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Connect to TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Replace with your IP and port

# Define the time range
start_date = datetime(2025, 1, 1, tzinfo=ZoneInfo('UTC'))  # January 1, 2025
end_date = datetime(2025, 4, 3 , tzinfo=ZoneInfo('UTC'))    # April 3, 2025

# Define the relevant contracts
contracts = [
    {'symbol': 'ES', 'exchange': 'CME', 'currency': 'USD', 'contract_month': '202503', 'roll_date': "20250318" },   # March 2025
    {'symbol': 'ES', 'exchange': 'CME', 'currency': 'USD', 'contract_month': '202506', 'roll_date': "20250618"}   # June 2025
]

# Function to fetch historical data for a contract
def fetch_contract_data(contract, start_date, end_date):
    # Create a contract object
    es_contract = Future(
        symbol=contract['symbol'],
        exchange=contract['exchange'],
        currency=contract['currency'],
        lastTradeDateOrContractMonth=contract['contract_month'],
        includeExpired=True   #This needs to be switched on for expired contracts    
    )

    # Fetch historical data
    bars = ib.reqHistoricalData(
        es_contract,
        endDateTime=end_date.strftime('%Y%m%d %H:%M:%S'),
        durationStr=f'{(end_date - start_date).days + 1} D',  # Duration in days
        barSizeSetting='5 mins',  # 5-minute bars
        whatToShow='TRADES',  # Use TRADES for actual trade data
        useRTH=0,  # All Trading hours
        formatDate=1,  # Format dates as Unix timestamps
        timeout = 600
    )

    # Convert bars to a pandas DataFrame
    df = util.df(bars)
    # append the contract month as a new column
    df['contract_month'] = contract['contract_month']
    return df

# Fetch data for each contract
data_frames = []
previous_roll_date = None  # Initialize previous roll date
for contract in contracts:
    print(f"Fetching data for {contract['contract_month']} contract...")
    # Fetch the contract data 
    df = fetch_contract_data(contract, start_date, end_date)
    if not df.empty:
        #for dates between start and first roll date, only include March contract
        if previous_roll_date:
            df = df[(df['date'] > previous_roll_date) & (df['date'] < contract['roll_date'])]
        else:
            df = df[(df['date'] >= start_date) & (df['date'] <= contract['roll_date'])]
        # append specific columns to the data frame
        df = df[['date', 'close', 'contract_month']]
        # Convert the date column to UTC
        df['date'] = pd.to_datetime(df['date'], unit='s', utc=True)
        # Shift the data forward by 5 minutes // hack to allign with bender data 
        df['date'] = df['date'] + pd.Timedelta(minutes=5)
        # Append the DataFrame to the list
        data_frames.append(df)
        # Update the previous roll date for the next contract
        previous_roll_date = contract['roll_date']
    else:
        print(f"No data returned for {contract['contract_month']} contract.")
        combined_df = pd.DataFrame()  # Empty DataFrame

# Combine the data (if any data was fetched)
if data_frames:
    combined_df = pd.concat(data_frames)
    combined_df = combined_df.sort_values('date')  # Sort by date
    print("Data fetched successfully!")
else:
    print("No data fetched for any contract.")
    combined_df = pd.DataFrame()  # Empty DataFrame

# Disconnect from IBKR
ib.disconnect()

# Save the data to a CSV file (if data was fetched)
if not combined_df.empty:
    combined_df.to_csv('ES_5min_YTD_UTC.csv', index=False)
    print("Data saved to 'ES_5min_YTD_UTC.csv'.")
else:
    print("No data to save.")