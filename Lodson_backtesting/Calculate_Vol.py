import pandas as pd

# Define historic 5m data for ES which we fetch from Fetch_historical_data_IBKR.py
Historical_filepath = 'C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\ES_5min_7_april.csv'

# Load the data
data = pd.read_csv(Historical_filepath, parse_dates=['date'])

# Convert 'date' column to datetime with utc=True
data['date'] = pd.to_datetime(data['date'], utc=True)

filtered_data = data[data['date'] >= '2023-12-17']

# Adjust the date by 1 hour seems like to_datetime() when UTC is true it shifts by 6 hours, we need an extra 1
filtered_data['date'] = filtered_data['date'] + pd.Timedelta(hours=1)

cleaned_price_data = filtered_data[['date', 'close']]

#define our time periods we want to calculate the volatility for
Time_period = {
    "4/7/2025 03:25:00": "4/7/2025 07:00:00"
}

# Create a new dictionary with datetime objects
Time_period_datetime = {
    pd.to_datetime(key, utc=True): pd.to_datetime(value, utc=True)
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