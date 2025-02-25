from ib_insync import IB, Order, Trade

# Initialize the IB connection
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Retrieve all executions (filled orders)
executions = ib.executions()

# Retrieve all open (pending) orders
open_orders = ib.reqOpenOrders()

# Display all executions (filled trades)
print("All Executions (Filled Trades):")
for exec in executions:
    trades = ib.trades()
    matching_trade = next((trade for trade in trades if trade.order.permId == exec.permId), None)

    if matching_trade:
        contract = matching_trade.contract
        print(f"Order Ref: {exec.orderRef if exec.orderRef else 'N/A'} | Symbol: {contract.symbol} | "
              f"Action: {exec.side} | Quantity: {exec.shares} | Price: {exec.avgPrice} | "
              f"Executed At: {exec.time} | Account: {exec.acctNumber} | Exchange: {exec.exchange} | "
              f"Liquidation: {exec.liquidation}")
    else:
        print(f"No trade found for execution {exec.execId}")

# Display all pending orders, if any
if open_orders:
    print("\nAll Pending Orders:")
    for order in open_orders:
        # Only process Order objects or Trade objects
        if isinstance(order, Order):
            contract = getattr(order, 'contract', None)
            if contract:
                print(f"Order Ref: {getattr(order, 'orderRef', 'N/A')} | Symbol: {contract.symbol} | "
                      f"Action: {getattr(order, 'action', 'N/A')} | "
                      f"Quantity: {getattr(order, 'totalQuantity', 'N/A')} | "
                      f"Price: {getattr(order, 'lmtPrice', 'N/A') if getattr(order, 'orderType', 'MKT') == 'LMT' else 'N/A'} | "
                      f"Status: {getattr(getattr(order, 'orderStatus', None), 'status', 'N/A')} | "
                      f"TIF: {getattr(order, 'tif', 'N/A')}")
        elif isinstance(order, Trade):
            # If it's a Trade object, get details from the trade and its status
            contract = order.contract
            order_details = order.order
            order_status = order.orderStatus
            print(f"Order Ref: {getattr(order_details, 'orderRef', 'N/A')} | Symbol: {contract.symbol} | "
                  f"Action: {order_details.action} | Quantity: {order_details.totalQuantity} | "
                  f"Price: {getattr(order_details, 'lmtPrice', 'N/A') if order_details.orderType == 'LMT' else 'N/A'} | "
                  f"Status: {order_status.status} | Filled: {order_status.filled} | Remaining: {order_status.remaining} | "
                  f"TIF: {getattr(order_details, 'tif', 'N/A')}")
        else:
            print(f"Encountered a non-Order object of type: {type(order)}")
            print(f"Object details: {order}")
else:
    print("\nNo pending orders.")

# Disconnect
ib.disconnect()
