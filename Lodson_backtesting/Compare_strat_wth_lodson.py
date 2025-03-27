import pandas as pd
from datetime import datetime

# Define historic 5m data for ES which we fetch from Fetch_historical_data_IBKR.py
Historical_filepath = 'C:\\Users\\Aaron\\ACCN\\Lodson_data\\ES_5min_all.csv'

# Load the data
data = pd.read_csv(Historical_filepath, parse_dates=['date'])

# Convert 'date' column to datetime with utc=True
data['date'] = pd.to_datetime(data['date'], utc=True)

# Strip timezone information
data['date'] = data['date'].dt.tz_localize(None)

filtered_data = data[data['date'] >= '2023-12-17']

# Adjust the date by 1 hour seems like to_datetime() when UTC is true it shifts by 6 hours, we need an extra 1
filtered_data['date'] = filtered_data['date'] + pd.Timedelta(hours=1)

# We need all these columns to calculate stochasitc and RSI values
cleaned_data = filtered_data[['date', 'close','low', 'high']]

# Define our  calculation for RSI, we just need to parse in close price
def calculate_rsi(cleaned_data, period=14):
    delta = cleaned_data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Define our calculation for Stochastic Oscillator using low and high prices over the defined period
# K = 100 * ((Close - Low) / (High - Low))
# D = 3-day SMA of K
def calculate_stochastic(cleaned_data, k_period=14, d_period=3):
    low_min = cleaned_data['low'].rolling(window=k_period).min()
    high_max = cleaned_data['high'].rolling(window=k_period).max()
    cleaned_data['K_14'] = 100 * ((cleaned_data['close'] - low_min) / (high_max - low_min))
    cleaned_data['D_3'] = cleaned_data['K_14'].rolling(window=d_period).mean()
    return cleaned_data

# Add RSI to our Cleaned Data
cleaned_data['RSI 14 Day'] = calculate_rsi(cleaned_data)

# Add Stochastic Oscillator to our Cleaned Data
cleaned_data = calculate_stochastic(cleaned_data)

#cleaned_data.to_csv('Cleaned_data_with_RSI_Stochastic.csv', index=False)


# Define entry and exit signals using RSI and Stochastic Oscillator
# Long Entry: RSI is oversold, and Stochastic shows a bullish crossover
cleaned_data['Long_Entry'] = (
    (cleaned_data['RSI 14 Day'] < 40) &  # RSI is oversold
    (cleaned_data['K_14'] > cleaned_data['D_3']) &  # Bullish crossover
    (cleaned_data['K_14'] < 50)  # Stochastic %K is in the lower range
)

# Short Entry: RSI is overbought, and Stochastic shows a bearish crossover
cleaned_data['Short_Entry'] = (
    (cleaned_data['RSI 14 Day'] > 55) &  # RSI is overbought
    (cleaned_data['K_14'] < cleaned_data['D_3']) &  # Bearish crossover
    (cleaned_data['K_14'] > 50)  # Stochastic %K is in the upper range
)

# Long Exit: RSI is no longer oversold, and Stochastic shows a bearish crossover
cleaned_data['Long_Exit'] = (
    (cleaned_data['RSI 14 Day'] > 50) &  # RSI is no longer oversold
    (cleaned_data['K_14'] < cleaned_data['D_3'])  # Bearish crossover
)

# Short Exit: RSI is no longer overbought, and Stochastic shows a bullish crossover
cleaned_data['Short_Exit'] = (
    (cleaned_data['RSI 14 Day'] < 45) &  # RSI is no longer overbought
    (cleaned_data['K_14'] > cleaned_data['D_3'])  # Bullish crossover
)

# Backtesting the strategy now

# Initialize a list to store trade details
trades = []

# Initialize variables for tracking the current position and trade number
current_position = None
entry_price = None
trade_number = 0

# Loop through the data to simulate trades
for i in range(len(cleaned_data)):
    # Check for long entry 
    if current_position is None:
        if cleaned_data['Long_Entry'].iloc[i]:
            trade_number += 1
            current_position = 'Long'
            entry_price = cleaned_data['close'].iloc[i]
            trades.append({
                'Trade #': trade_number,
                'Trade Type': 'Entry long',
                'Date': cleaned_data['date'].iloc[i],
                'Price': entry_price,
                'Profit': '-'
            })
       
    # Check for short entry
    elif current_position is None:
        if cleaned_data['Short_Entry'].iloc[i]:
            trade_number += 1
            current_position = 'Short'
            entry_price = cleaned_data['close'].iloc[i]
            trades.append({
                'Trade #': trade_number,
                'Trade Type': 'Entry short',
                'Date': cleaned_data['date'].iloc[i],
                'Price': entry_price,
                'Profit': '-'
            })

    # Check for long exit (e.g., RSI > 50)
    elif current_position == 'Long':
        if cleaned_data['Long_Exit'].iloc[i]:
            exit_price = cleaned_data['close'].iloc[i]
            profit = (exit_price - entry_price) * 200
            trades.append({
                'Trade #': trade_number,
                'Trade Type': 'Exit long',
                'Date': cleaned_data['date'].iloc[i],
                'Price': exit_price,
                'Profit': f"{profit:,.0f}"
            })
        current_position = None
        entry_price = None

    # Check for short exit (e.g., RSI < 50)
    elif current_position == 'Short':
        if cleaned_data['Short_Exit'].iloc[i]:
            exit_price = cleaned_data['close'].iloc[i]
            profit = (entry_price - exit_price) * 200
            trades.append({
                'Trade #': trade_number,
                'Trade Type': 'Exit short',
                'Date': cleaned_data['date'].iloc[i],
                'Price': exit_price,
                'Profit': f"{profit:,.0f}"
            })
        current_position = None
        entry_price = None

# Count the number of signals
print("Long Entries:", cleaned_data['Long_Entry'].sum())
print("Short Entries:", cleaned_data['Short_Entry'].sum())
print("Long Exits:", cleaned_data['Long_Exit'].sum())
print("Short Exits:", cleaned_data['Short_Exit'].sum())

# Convert the trades list to a dataframe
Aaron_Strategy_trades = pd.DataFrame(trades)

##trades_df.to_csv('Aaron_backtest_trade_history.csv', index=False)

"Now we are going to compare this to Lodson's trades"

# Load Lodson's trades data
Lodson_trades = pd.read_csv('C:\\Users\\Aaron\\ACCN\\Lodson_data\\Lodson_trade_history_with_oscilators.csv')

# Replace 'Date' with the matching column name in Lodson's trades data
Aaron_Strategy_trades = Aaron_Strategy_trades.rename(columns={'Date': 'Date/Time'}) 

# Replace 'Trade Type' with 'Type' in my trades data, bit of a hack but it works
Aaron_Strategy_trades = Aaron_Strategy_trades.rename(columns={'Trade Type': 'Type'}) 

# Convert Data types to datetime
Lodson_trades['Date/Time'] = pd.to_datetime(Lodson_trades['Date/Time'])

Lodson_trades = Lodson_trades[Lodson_trades['Date/Time'] >= '2023-12-17']

# Clean and convert 'Price' in Lodson_trades
Lodson_trades['Price'] = (
    Lodson_trades['Price']
    .str.replace(',', '')
    .str.replace('$', '')
    .str.strip()
)
Lodson_trades['Price'] = pd.to_numeric(Lodson_trades['Price'])
# Merge the data on 'Date/Time'
merged_data = pd.merge(
    Lodson_trades, 
    Aaron_Strategy_trades, 
    on='Date/Time', 
    how='left', 
    suffixes=('_Lodson', '_Aaron')
)

# Define a tolerance for price comparison
price_tolerance = 1

# Check for matching trades
merged_data['Match'] = (
    (merged_data['Type_Lodson'] == merged_data['Type_Aaron']) &  # Trade type matches
    (abs(merged_data['Price_Lodson'] - merged_data['Price_Aaron']) <= price_tolerance)  # Price matches
)

# Display the merged data
print(merged_data.tail())

"Analytics of the backtest"
# Count matching trades
matching_trades = merged_data['Match'].sum()

# Filter mismatched trades
mismatched_trades = merged_data[merged_data['Match'] == False]

# Display mismatched trades
print(mismatched_trades[['Date/Time', 'Type_Lodson', 'Price_Lodson', 'Type_Aaron', 'Price_Aaron']])

# Total number of Lodson's trades
total_trades = len(Lodson_trades)

# Calculate accuracy
accuracy = (matching_trades / total_trades) * 100

print(f"Accuracy: {accuracy:.2f}%")


