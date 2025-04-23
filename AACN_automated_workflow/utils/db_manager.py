import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('trades.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            ib_order_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def write_trade(symbol, action, price, quantity, ib_order_id=None):
    conn = sqlite3.connect('trades.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (symbol, action, price, quantity, timestamp, ib_order_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (symbol, action, price, quantity, datetime.now(), ib_order_id))
    conn.commit()
    conn.close()
