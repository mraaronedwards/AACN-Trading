# utils/queue_manager.py
import queue

# Create a global queue for communication
trade_queue = queue.Queue()

def add_to_queue(data):
    trade_queue.put(data)

def get_from_queue():
    try:
        return trade_queue.get_nowait()
    except queue.Empty:
        return None