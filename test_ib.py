#test connection to IB
from ib_insync import IB

print("testing connection \n")

# Initialize IB connection
ib = IB()

# Connect to TWS (default port is 7497 for paper trading)
# Change to 7496 for live trading if needed
ib.connect('192.168.0.241', 7497, clientId=1)

# Fetch trade history
trades = ib.trades()
orders = ib.orders()


# Retrieve executions, which contain the filled order status
executions = ib.executions()


# Print executed trades which have been either filled or cancelled
for trade in trades:
    print(f"Trade: {trade.contract.symbol} | Action: {trade.order.action} | Quantity: {trade.order.totalQuantity} | Status: {trade.orderStatus.status}")


# Display today's executions with contract information
for exec in executions:
    # Retrieve the order associated with this execution using the orderId
    order = ib.order(exec.orderId)
    
    # Access the contract from the order
    contract = order.contract  # Contract associated with the order
    
    print(f"Order Ref: {exec.orderRef} | Symbol: {contract.symbol} | Action: {exec.side} | "
          f"Quantity: {exec.shares} | Price: {exec.avgPrice} | Executed At: {exec.time} | "
          f"Account: {exec.acctNumber} | Exchange: {exec.exchange} | Liquidation: {exec.liquidation}")


# Disconnect from TWS
ib.disconnect()
