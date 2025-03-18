from ib_insync import *
import pandas as pd
from datetime import datetime

# Connect to TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Replace with your IP and port

# Define the time range
start_date = datetime(2023, 11, 5)  # November 6, 2023
end_date = datetime(2024, 2, 18)    # February 17, 2024

# Define the relevant contracts
contracts = [
    {'symbol': 'ES', 'exchange': 'CME', 'currency': 'USD', 'contract_month': '202312'},  # December 2023
    {'symbol': 'ES', 'exchange': 'CME', 'currency': 'USD', 'contract_month': '202403'}   # March 2024
]

# Function to fetch historical data for a contract
def fetch_contract_data(contract, start_date, end_date):

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
    return df

# Fetch data for each contract
data_frames = []
for contract in contracts:
    print(f"Fetching data for {contract['contract_month']} contract...")
    df = fetch_contract_data(contract, start_date, end_date)
    if not df.empty:
        data_frames.append(df)
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
    combined_df.to_csv('ES_5min_all.csv', index=False)
    print("Data saved to 'ES_5min_all.csv'.")
else:
    print("No data to save.")