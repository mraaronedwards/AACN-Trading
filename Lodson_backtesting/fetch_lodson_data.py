import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the TradingView strategy
url = "https://www.tradingview.com/script/XZNqePGs-ES-Lodson-5m-1-0/"

# Send a GET request to the page
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Locate the "List of Trades" section
trades_section = soup.find('div', {'class': 'trades-section'})  # Adjust the class name based on the page structure

if not trades_section:
    raise Exception("Could not find the 'List of Trades' section on the page.")

# Extract the trades table
trades_table = trades_section.find('table')
if not trades_table:
    raise Exception("Could not find the trades table in the section.")

# Parse the table into a DataFrame
rows = trades_table.find_all('tr')
data = []
for row in rows:
    cols = row.find_all('td')
    cols = [col.text.strip() for col in cols]
    data.append(cols)

# Convert to DataFrame
tradingview_trades = pd.DataFrame(data[1:], columns=data[0])