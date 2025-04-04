import pandas as pd

# Define historic 5m data for ES which we fetch from Fetch_historical_data_IBKR.py
Historical_filepath = 'C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\ES_5min_YTD_UTC.csv'

# Load the data
data = pd.read_csv(Historical_filepath, parse_dates=['date'])

cleaned_price_data = data[['date', 'close']]

# Load Lodson's trades data
Lodson_trades = pd.read_csv('C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\Bender_YTD_messages.csv')

# Convert Data types to datetime
#Lodson_trades['Date/Time'] = pd.to_datetime(Lodson_trades['Date/Time'])

#Lodson_trades = Lodson_trades[Lodson_trades['Date/Time'] >= '2023-12-17']
Lodson_trades['fill_price'] = pd.to_numeric(Lodson_trades['fill_price'])

#Sort Lodson trades by date and trade type
Lodson_trades = Lodson_trades.sort_values(by=['timestamp'], ascending=[True])

# Iterate through Lodson trades and if there is a match on date and type is Entry Long or Entry Short, then we will check the next price in cleaned data untill a predefined tolerance is met
# If the price is within the tolerance then we will continue to iterate untill the next Exit Long or Exit Short is found
# If the price is not within the tolerance then we will print out the price and calculate the profit or loss
# We will have 5 tolerances: 20, 30, 50, 80, 100 tick tolerance

# Define a tolerance for price comparison
tolerances = [20, 30, 50, 80, 100, 6000]
price_tolerance = tolerances

#intialise a trade list to store the trades
trades = []


### Convert the 'timestamp' column to datetime
Lodson_trades['timestamp'] = pd.to_datetime(Lodson_trades['timestamp'], utc=True)


# Define a function to calculate volatility between two dates for a range of prices
def calculate_volatility(start_date, end_date, cleaned_price_data):
    # Filter the data for the time period
    period_data = cleaned_price_data[(cleaned_price_data['date'] >= start_date) & (cleaned_price_data['date'] <= end_date)]
    
    # Calculate the volatility
    volatility = period_data['close'].std()
    return volatility


for tolerance in price_tolerance:
    # Loop through the data to Lodson trades
    print(f"Checking trades with tolerance: {tolerance}")
    for i in range(len(Lodson_trades)):
        print(f"Checking trade: {Lodson_trades.iloc[i]}")
        # Check for Long entry
        if Lodson_trades['order_type'].iloc[i] == 'buy':
            print(f"Found long entry trade: {Lodson_trades.iloc[i]}")
            # Find the matching price entry in cleaned data and iterate through untill price breaks the tolerance
            for j in range(len(cleaned_price_data)):
                # Check if the date matches in both dataframes if it does then check the next price untill the tolerance is broken
                if abs((Lodson_trades['timestamp'].iloc[i] - cleaned_price_data['date'].iloc[j]).total_seconds()) <= 300:
                    # Check the next price untill the tolerance is broken
                    for k in range(j, len(cleaned_price_data)):
                        market_price = cleaned_price_data.iloc[k]
                        Lodson_trade = Lodson_trades.iloc[i]
                        Lodson_trade_T1 = Lodson_trades.iloc[i+1] 
                        if  (Lodson_trades['fill_price'].iloc[i] - cleaned_price_data['close'].iloc[k] < tolerance) & (cleaned_price_data['date'].iloc[k] < Lodson_trades['timestamp'].iloc[i+1]):
                            continue
                        elif (cleaned_price_data['date'].iloc[k] >= Lodson_trades['timestamp'].iloc[i+1]):
                            print("Stop loss not iniated, proft taken by Lodson trade:\n")
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Long',
                            'Opening Date': Lodson_trades['timestamp'].iloc[i],
                            'Open Price': Lodson_trades['fill_price'].iloc[i],
                            'Closing Date': Lodson_trades['timestamp'].iloc[i],
                            'Closing Price': Lodson_trades['fill_price'].iloc[i+1],
                            'Stop loss?': 'No',
                            'Profit': (Lodson_trades['fill_price'].iloc[i+1] - Lodson_trades['fill_price'].iloc[i] )*200,
                            'Tolerance': tolerance,
                            'Realised volatility': calculate_volatility(Lodson_trades['timestamp'].iloc[i], Lodson_trades['timestamp'].iloc[i+1], cleaned_price_data),
                            })
                            break
                        elif ( Lodson_trades['fill_price'].iloc[i] - cleaned_price_data['close'].iloc[k] >= tolerance):
                            print("Stop loss iniated, exiting this position:\n")
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Long',
                            'Opening Date': Lodson_trades['timestamp'].iloc[i],
                            'Open Price': Lodson_trades['fill_price'].iloc[i],
                            'Closing Date': cleaned_price_data['date'].iloc[k],
                            'Closing Price': cleaned_price_data['close'].iloc[k],
                            'Stop loss?': 'Yes',
                            'Profit': (cleaned_price_data['close'].iloc[k] - Lodson_trades['fill_price'].iloc[i])*200,
                            'Tolerance': tolerance,
                            'Realised volatility': calculate_volatility(Lodson_trades['timestamp'].iloc[i], cleaned_price_data['date'].iloc[k], cleaned_price_data),
                            })
                            break
                    break
        # Check for short entry
        elif Lodson_trades['order_type'].iloc[i] == 'sell':
            print(f"Found short entry trade: {Lodson_trades.iloc[i]}")
            # Find the matching price entry in cleaned data and iterate through untill price breaks the tolerance
            for j in range(len(cleaned_price_data)):
                # Check if the date matches in both dataframes if it does then check the next price untill the tolerance is broken
                if abs((Lodson_trades['timestamp'].iloc[i] - cleaned_price_data['date'].iloc[j]).total_seconds()) <= 300:
                    # Check the next price untill the tolerance is broken
                    for k in range(j, len(cleaned_price_data)):
                        market_price = cleaned_price_data.iloc[k]
                        Lodson_trade = Lodson_trades.iloc[i]
                        Lodson_trade_T1 = Lodson_trades.iloc[i+1]
                        if  (cleaned_price_data['close'].iloc[k] - Lodson_trades['fill_price'].iloc[i] <= tolerance) & (cleaned_price_data['date'].iloc[k] < Lodson_trades['timestamp'].iloc[i+1]):
                            continue
                        elif (cleaned_price_data['date'].iloc[k] >= Lodson_trades['timestamp'].iloc[i+1]):
                            print("Stop loss not iniated, proft taken by Lodson trade:\n")
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Short',
                            'Opening Date': Lodson_trades['timestamp'].iloc[i],
                            'Open Price': Lodson_trades['fill_price'].iloc[i],
                            'Closing Date': Lodson_trades['timestamp'].iloc[i+1],
                            'Closing Price': Lodson_trades['fill_price'].iloc[i+1],
                            'Stop loss?': 'No',
                            'Profit': (  Lodson_trades['fill_price'].iloc[i] - Lodson_trades['fill_price'].iloc[i+1] )*200,
                            'Tolerance': tolerance,
                            'Realised volatility': calculate_volatility(Lodson_trades['timestamp'].iloc[i], Lodson_trades['timestamp'].iloc[i+1], cleaned_price_data),
                            })
                            break
                        elif (cleaned_price_data['close'].iloc[k] - Lodson_trades['fill_price'].iloc[i] >= tolerance):
                            print("Stop loss iniated, exiting this position:\n")
                            trades.append({
                            'Trade #': i,
                            'Trade Type': 'Short',
                            'Opening Date': Lodson_trades['timestamp'].iloc[i],
                            'Open Price': Lodson_trades['fill_price'].iloc[i],
                            'Closing Date': cleaned_price_data['date'].iloc[k],
                            'Closing Price': cleaned_price_data['close'].iloc[k],
                            'Stop loss?': 'Yes',
                            'Profit': ( Lodson_trades['fill_price'].iloc[i] - cleaned_price_data['close'].iloc[k])*200,
                            'Tolerance': tolerance,
                            'Realised volatility': calculate_volatility(Lodson_trades['timestamp'].iloc[i], cleaned_price_data['date'].iloc[k], cleaned_price_data),
                            })
                            break
                    break

print(trades)

# Convert the trades list to a DataFrame
trades_df = pd.DataFrame(trades)

# Save the trades to a CSV file
trades_df.to_csv('C:\\Users\\Aaron\\ACCN\\Lodson_backtesting\\Lodson_trades_with_stop_loss_YTD.csv', index=False)

#plot the profit with respect to time, overlay with the different tolerance thresholds

