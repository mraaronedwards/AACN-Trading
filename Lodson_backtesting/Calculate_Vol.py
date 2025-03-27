import pandas as pd

# Define historic 5m data for ES which we fetch from Fetch_historical_data_IBKR.py
Historical_filepath = 'C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\ES_5min_all.csv'

# Load the data
data = pd.read_csv(Historical_filepath, parse_dates=['date'])

# Convert 'date' column to datetime with utc=True
data['date'] = pd.to_datetime(data['date'], utc=True)

# Strip timezone information
data['date'] = data['date'].dt.tz_localize(None)

filtered_data = data[data['date'] >= '2023-12-17']

# Adjust the date by 1 hour seems like to_datetime() when UTC is true it shifts by 6 hours, we need an extra 1
filtered_data['date'] = filtered_data['date'] + pd.Timedelta(hours=1)

cleaned_price_data = filtered_data[['date', 'close']]

#define our time periods we want to calculate the volatility for
Time_period = {
    "1/4/2024 21:15:00": "1/5/2024 15:30:00",
    "2/2/2024 4:30:00": "2/2/2024 19:10:00",
    "2/5/2024 1:15:00" : "2/5/2024 20:45:00",
    "2/14/2024 15:00:00": "2/15/2024 0:35:00",
    "1/10/2024 14:35:00": "1/10/2024 21:00:00",
    "1/8/2024 15:45:00": "1/9/2024 2:00:00",
    "2/12/2024 21:25:00": "2/14/2024 1:20:00",
    
    "1/29/2024 4:40:00": "1/30/2024 3:35:00",
    "1/31/2024 13:40:00": "2/1/2024 3:10:00",
    "2/1/2024 21:30:00": "2/2/2024 4:30:00",
    "2/12/2024 21:25:00": "2/14/2024 1:20:00",
}

# Create a new dictionary with datetime objects
Time_period_datetime = {
    pd.to_datetime(key): pd.to_datetime(value) 
    for key, value in Time_period.items()
}

# Update the Time_period dictionary
Time_period = Time_period_datetime

# Calculate the volatility for each time period
for start, end in Time_period.items():
    # Filter the data for the time period
    period_data = cleaned_price_data[(cleaned_price_data['date'] >= start) & (cleaned_price_data['date'] <= end)]
    
    # Calculate the volatility
    volatility = period_data['close'].std()
    print(f"Volatility for {start} - {end}: {volatility:.2f}")