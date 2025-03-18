# ui/app.py
from flask import Flask, render_template, jsonify, request
from utils.state_manager import get_bot_state, set_bot_state, get_ibkr_connection_status
from utils.logging_utils import get_logs

app = Flask(__name__)

@app.route('/')
def index():
    """
    Render the main UI page.
    """
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    """
    Return the current status of the bot and IBKR connection.
    """
    return jsonify({
        "bot_status": get_bot_state(),
        "ibkr_connected": get_ibkr_connection_status()
    })

@app.route('/pause', methods=['POST'])
def pause():
    """
    Pause the bot.
    """
    set_bot_state("paused")
    return jsonify({"status": "success", "message": "Bot paused"})

@app.route('/resume', methods=['POST'])
def resume():
    """
    Resume the bot.
    """
    set_bot_state("running")
    return jsonify({"status": "success", "message": "Bot resumed"})

@app.route('/logs', methods=['GET'])
def logs():
    """
    Return the latest logs.
    """
    logs = get_logs()
    return jsonify({"logs": logs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)