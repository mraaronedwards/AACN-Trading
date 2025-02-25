from ib_insync import IB, Option
from datetime import datetime

# Initialize the IB connection
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Get today's date in the required format (YYYYMMDD)
today = datetime.now().strftime('%Y%m%d')

# Use reqMatchingSymbols to search for SPX options
matching_symbols = ib.reqMatchingSymbols('SPX')

# Filter matching symbols for 'SPXPM' (PM session)
filtered_symbols = [symbol for symbol in matching_symbols if 'SPXPM' in symbol.contract.symbol]

# Iterate over filtered symbols and request detailed option contract info
for symbol in filtered_symbols:
    contract = Option(
        symbol='SPX',                  # Symbol for the options contract
        lastTradeDateOrContractMonth=today,  # Filter by today's expiration
        exchange='CBOE',                # Exchange for SPX options
        currency='USD',                 # Currency for SPX options
        localSymbol=symbol.contract.symbol,  # Get the local symbol
        strike=5955.0,                  # Example strike price (adjust based on your needs)
        right='P'                       # Example: Put option (adjust as needed)
    )
    
    contract_details = ib.reqContractDetails(contract)

    if contract_details:
        for details in contract_details:
            print(f"Found contract: {details.contract.localSymbol} | Expiry: {details.contract.lastTradeDateOrContractMonth}")
    else:
        print(f"No contract details found for {symbol.contract.symbol}")

# Disconnect after fetching details
ib.disconnect()
