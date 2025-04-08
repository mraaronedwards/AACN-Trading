from ib_insync import *
from datetime import datetime

# Initialize the IB connection
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

def get_nearest_future_contract(ib, symbol):
    """
    Fetch the nearest expiry future contract for the given symbol.
    """
    # Define a generic future contract
    contract = Future(symbol=symbol)
    
    # Fetch contract details
    contracts = ib.reqContractDetails(contract)
    
    if not contracts:
        raise ValueError(f"No contracts found for symbol: {symbol}")
    
    # Find the contract with the nearest expiry
    nearest_contract = min(
        contracts,
        key=lambda x: datetime.strptime(x.contract.lastTradeDateOrContractMonth, "%Y%m%d")
    )
    return nearest_contract.contract

nearest_contract = get_nearest_future_contract(ib, 'MES')
print(nearest_contract)
