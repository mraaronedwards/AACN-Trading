import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

# Load the trade data
Lodson_filepath = 'C:\\Users\\Aaron\\ACCN\\Lodson_data\\es-trading-data.csv'
Historical_filepath = 'C:\\Users\\Aaron\\ACCN\\Lodson_data\\ES_5min.csv'
actual_trades = pd.read_csv(Lodson_filepath)  


# Clean and format the data
actual_trades['Date/Time'] = pd.to_datetime(actual_trades['Date/Time'])
# Remove commas from the 'Price' column and convert to float
actual_trades['Price'] = actual_trades['Price'].str.replace(',', '').str.replace('USD', '').astype(float)
actual_trades['Position'] = actual_trades['Signal'].map({'L': 'Long', 'S': 'Short'})

# Select relevant columns
actual_trades = actual_trades[['Date/Time', 'Price', 'Position']]
actual_trades.columns = ['Timestamp', 'Entry Price', 'Position']

# now testing the against real data
# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Load historical data (replace with your data source)
data = pd.read_csv(Historical_filepath, parse_dates=['Date'], index_col='Date')

# Calculate RSI
data['RSI'] = calculate_rsi(data, period=14)

# Define overbought and oversold thresholds
overbought = 70
oversold = 30

# Generate signals
data['Signal'] = 0
data['Signal'][data['RSI'] < oversold] = 1  # Buy signal (oversold)
data['Signal'][data['RSI'] > overbought] = -1  # Sell signal (overbought)

# Ensure the strategy is always in the market
data['Position'] = data['Signal'].replace(0, method='ffill')

# Generate trades from the assumed strategy
assumed_trades = data[data['Position'].diff() != 0][['Position']].reset_index()
assumed_trades = assumed_trades.rename(columns={'Date': 'Timestamp'})
assumed_trades['Position'] = assumed_trades['Position'].map({1: 'Long', -1: 'Short', 0: 'Exit'})

# Align the timestamps
# Define a time tolerance for matching trades
tolerance = timedelta(minutes=5)

# Initialize a list to store matched trades
matched_trades = []

# Iterate through actual trades and find the closest match in assumed trades
for actual_trade in actual_trades.itertuples():
    closest_match = None
    min_diff = None
    
    for assumed_trade in assumed_trades.itertuples():
         # Remove timezone from assumed_trade.Timestamp
        assumed_timestamp = assumed_trade.Timestamp.tz_localize(None)

        time_diff = abs(actual_trade.Timestamp - assumed_timestamp)

        if time_diff <= tolerance:
            if min_diff is None or time_diff < min_diff:
                closest_match = assumed_trade
                min_diff = time_diff
    
    if closest_match:
        matched_trades.append({
            'Actual Timestamp': actual_trade.Timestamp,
            'Assumed Timestamp': closest_match.Timestamp,
            'Actual Position': actual_trade.Position,
            'Assumed Position': closest_match.Position,
            'Time Difference': min_diff
        })

# Convert matched trades to a DataFrame
matched_trades_df = pd.DataFrame(matched_trades)

# Calculate accuracy
matched_trades_df['Match'] = matched_trades_df['Actual Position'] == matched_trades_df['Assumed Position']
accuracy = matched_trades_df['Match'].sum() / len(matched_trades_df)
print(f"Accuracy: {accuracy:.2%}")

print(f"Actual trades: {len(actual_trades)} rows")
print(f"Assumed trades: {len(assumed_trades)} rows")
print("Actual trades timestamps:")
print(actual_trades['Timestamp'].head())
print("Assumed trades timestamps:")
print(assumed_trades['Timestamp'].tail())

print("Actual trades:")
print(actual_trades.head())
print("Assumed trades:")
print(assumed_trades.tail())

plt.figure(figsize=(12, 6))
plt.plot(data['Close'], label='Price', alpha=0.5)

# Plot actual trades
plt.scatter(
    actual_trades['Timestamp'],
    actual_trades['Entry Price'],
    color='green',
    label='Actual Trades',
    marker='^',
    alpha=0.7
)

# Plot assumed trades
plt.scatter(
    assumed_trades['Timestamp'],
    data.loc[assumed_trades['Timestamp'], 'Close'],
    color='blue',
    label='Assumed Trades',
    marker='o',
    alpha=0.7
)

plt.legend()
plt.show()
