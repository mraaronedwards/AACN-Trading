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

#cleaned_data.to_csv('Cleaned_data_with_RSI_Stochastic.csv', index=False)
# Load Lodson's trades data
Lodson_trades = pd.read_csv('C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\Lodson_trade_history_with_oscilators.csv')

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

#Sort Lodson trades by date and trade type
Lodson_trades = Lodson_trades.sort_values(by=['Trade #', 'Type'], ascending=[True, True])

print(Lodson_trades.head())
print(Lodson_trades.tail())
# Iterate through Lodson trades and if there is a match on date and type is Entry Long or Entry Short, then we will check the next price in cleaned data untill a predefined tolerance is met
# If the price is within the tolerance then we will continue to iterate untill the next Exit Long or Exit Short is found
# If the price is not within the tolerance then we will print out the price and calculate the profit or loss
# We will have 5 tolerances: 20, 30, 50, 80, 100 tick tolerance

# Define a tolerance for price comparison
tick_size = 0.25
tolerances = [20, 30, 50, 80, 100]
price_tolerance = [tolerance * tick_size for tolerance in tolerances]

#intialise a trade list to store the trades
trades = []

for tolerance in price_tolerance:
    # Loop through the data to Lodson trades
    print(f"Checking trades with tolerance: {tolerance}")
    for i in range(len(Lodson_trades)):
        print(f"Checking trade: {Lodson_trades.iloc[i]}")
        # Check for short entry 
        if Lodson_trades['Type'].iloc[i] == 'Entry short':
            print(f"Found short entry trade: {Lodson_trades.iloc[i]}")
            # Find the matching price entry in cleaned data and iterate through untill price breaks the tolerance
            for j in range(len(cleaned_price_data)):
                # Check if the date matches in both dataframes if it does then check the next price untill the tolerance is broken
                if Lodson_trades['Date/Time'].iloc[i] == cleaned_price_data['date'].iloc[j]:
                    # Check the next price untill the tolerance is broken
                    for k in range(j, len(cleaned_price_data)):
                        market_price = cleaned_price_data.iloc[k]
                        Lodson_trade = Lodson_trades.iloc[i]
                        Lodson_trade_T1 = Lodson_trades.iloc[i+1] 
                        if  (cleaned_price_data['close'].iloc[k] - Lodson_trades['Price'].iloc[i] <= tolerance) & (cleaned_price_data['date'].iloc[k] < Lodson_trades['Date/Time'].iloc[i+1]):
                            continue
                        elif (cleaned_price_data['date'].iloc[k] >= Lodson_trades['Date/Time'].iloc[i+1]):
                            print("Stop loss not iniated, proft taken by Lodson trade:\n")
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Short',
                            'Opening Date': Lodson_trades['Date/Time'].iloc[i],
                            'Open Price': Lodson_trades['Price'].iloc[i],
                            'Closing Date': Lodson_trades['Date/Time'].iloc[i],
                            'Closing Price': Lodson_trades['Price'].iloc[i+1],
                            'Stop loss?': 'No',
                            'Profit': (Lodson_trades['Price'].iloc[i] - Lodson_trades['Price'].iloc[i+1])*200,
                            'Tolerance': tolerance,
                            })
                            break
                        elif (cleaned_price_data['close'].iloc[k] - Lodson_trades['Price'].iloc[i] > tolerance):
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Short',
                            'Opening Date': Lodson_trades['Date/Time'].iloc[i],
                            'Open Price': Lodson_trades['Price'].iloc[i],
                            'Closing Date': cleaned_price_data['date'].iloc[k],
                            'Closing Price': cleaned_price_data['close'].iloc[k],
                            'Stop loss?': 'Yes',
                            'Profit': (Lodson_trades['Price'].iloc[i] - cleaned_price_data['close'].iloc[k])*200,
                            'Tolerance': tolerance,
                            })
                            break
                    break
        # Check for long entry
        elif Lodson_trades['Type'].iloc[i] == 'Entry long':
            print(f"Found long entry trade: {Lodson_trades.iloc[i]}")
            # Find the matching price entry in cleaned data and iterate through untill price breaks the tolerance
            for j in range(len(cleaned_price_data)):
                # Check if the date matches in both dataframes if it does then check the next price untill the tolerance is broken
                if Lodson_trades['Date/Time'].iloc[i] == cleaned_price_data['date'].iloc[j]:
                    # Check the next price untill the tolerance is broken
                    for k in range(j, len(cleaned_price_data)):
                        market_price = cleaned_price_data.iloc[k]
                        Lodson_trade = Lodson_trades.iloc[i]
                        Lodson_trade_T1 = Lodson_trades.iloc[i+1]
                        if  (Lodson_trades['Price'].iloc[i] - cleaned_price_data['close'].iloc[k] < tolerance) & (cleaned_price_data['date'].iloc[k] < Lodson_trades['Date/Time'].iloc[i+1]):
                            continue
                        elif (cleaned_price_data['date'].iloc[k] >= Lodson_trades['Date/Time'].iloc[i+1]):
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Long',
                            'Opening Date': Lodson_trades['Date/Time'].iloc[i],
                            'Open Price': Lodson_trades['Price'].iloc[i],
                            'Closing Date': Lodson_trades['Date/Time'].iloc[i+1],
                            'Closing Price': Lodson_trades['Price'].iloc[i+1],
                            'Stop loss?': 'No',
                            'Profit': (Lodson_trades['Price'].iloc[i+1] - Lodson_trades['Price'].iloc[i])*200,
                            'Tolerance': tolerance,
                            })
                            break
                        elif (Lodson_trades['Price'].iloc[i] - cleaned_price_data['close'].iloc[k] >= tolerance):
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Long',
                            'Opening Date': Lodson_trades['Date/Time'].iloc[i],
                            'Open Price': Lodson_trades['Price'].iloc[i],
                            'Closing Date': cleaned_price_data['date'].iloc[k],
                            'Closing Price': cleaned_price_data['close'].iloc[k],
                            'Stop loss?': 'Yes',
                            'Profit': (cleaned_price_data['close'].iloc[k] - Lodson_trades['Price'].iloc[i])*200,
                            'Tolerance': tolerance,
                            })
                            break

print(trades)

# Convert the trades list to a DataFrame
trades_df = pd.DataFrame(trades)

# Save the trades to a CSV file
trades_df.to_csv('C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\Lodson_trades_with_stop_loss.csv', index=False)

#plot the profit with respect to time, overlay with the different tolerance thresholds

