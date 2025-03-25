from typing import Dict, Any
from pprint import pprint
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load configuration from environment variables
app.config.from_prefixed_env()

# Set listen port from environment variable or assign default. The environment
# variable is "FLASK_PORT". The internal Flask mechanism removes the "FLASK_" prefix.
listen_port = app.config["PORT"] if 'PORT' in app.config else 8000

SECURITY_TOKEN = "vTUawjrPJFAQU0amkINfkjgavSgwIGPCX379DaknoTxF2w7CHMssJdTzxoRUgjFM"
TIMEFRAME = 15
# Variable to store the latest received data
latest_data = None

volumes = dict() #Dict[str, Dict[int, Dict[int, Dict[int, Any]]]]
tickers = ('WIN1!', 'NDX')

def assemble_volume_dict():
    global volumes, tickers

    volumes = {}
    for key in tickers:
        volumes[key] = dict.fromkeys(range(0, 24), dict())

    for ticker, hours in volumes.items():
        for hour in hours.keys():
            volumes[ticker][hour] = dict.fromkeys(range(0, 60), 0)

    # app.logger.info(volumes)


def is_local_request(request):
    return request.url_root.startswith('http://localhost') or request.url_root.startswith('http://127.0.0.1')


def validate_token(request):
    """
    Validate the security token in the request headers.
    """
    # Get the token from the request headers
    token = request.args.get("token")

    # Check if the token is valid
    if token == SECURITY_TOKEN:
        return True
    return False


def set_ticker_volume(ticker, hour, minute, second, volume):
    app.logger.info(f"Updating {ticker} {hour}:{minute}:{second} with {volume}")
    if second == 0:
        if minute == 0:
            minute = 59
        minute -= 1
    volumes[ticker][hour][int(minute)] += int(volume) 
    #app.logger.info(pprint.pformat(volumes, width=1))


@app.route('/volume', methods=['POST'])
def webhook():
    global latest_data

    local_request = is_local_request(request)
    valid_token = validate_token(request)
    
    # Validate the security token
    if not local_request and not valid_token:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # Get the JSON data from the POST request
    data = request.json
    # format date received
    dt = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
    dt = dt + timedelta(seconds=TIMEFRAME)
    # apply utc
    _ticker = data['ticker']

    set_ticker_volume(_ticker, dt.hour, dt.minute, dt.second, data['volume'])

    # Store the latest data
    latest_data = data

    # Log the received data (optional)
    app.logger.info(f"Received data: {data}")

    # Return a success response
    return jsonify({"status": "success", "message": "Data received"}), 200


@app.route('/last/datetime/<symbol>', methods=['GET'])
def server_time(symbol):
    global volumes

    local_request = is_local_request(request)
    valid_token = validate_token(request)

    # Validate the security token
    if not local_request and not valid_token:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    hours = volumes[symbol]
    hour_minute = None

    # Iterate through the hours in reverse order
    for hour in sorted(hours.keys(), reverse=True):
        # Iterate through the minutes in reverse order
        for minute in sorted(hours[hour].keys(), reverse=True):
            if hours[hour][minute] != 0:
                hour_minute = [hour, minute]
                break  # Stop searching once the latest non-zero is found
        if hour_minute:
            break  # Stop searching once the latest non-zero is found

    resp = (
            jsonify({'hour': hour_minute[0], 'minute': hour_minute[1]})
            if hour_minute else jsonify({'hour':0, 'minute':0})
            )

    # Grab the latest datetime already stored
    app.logger.info(resp.json)

    # Return the latest data
    return resp, 200


@app.route('/volume/<symbol>/<hour>/<minute>', methods=['GET'])
def get_latest_data(symbol, hour, minute):
    global latest_data
    # set static symbol name for now
    # symbol = 'WIN1!'

    local_request = is_local_request(request)
    valid_token = validate_token(request)

    # Validate the security token
    if not local_request and not valid_token:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = volumes[symbol][int(hour)][int(minute)]
    resp = jsonify({"status": "success", "data": data})

    app.logger.info(data)

    # Return the latest data
    return resp, 200


@app.route('/volume/M1/<symbol>/<hour>/<minute>', methods=['GET'])
def get_1m_volume(symbol, hour, minute):
    return get_latest_data(symbol, hour, minute)


@app.route('/volume/M5/<symbol>/<hour>/<minute>', methods=['GET'])
def get_5m_volume(symbol, hour, minute):
    """
    Returns the sum of volume for the last five minutes
    """
    global volumes

    # Validate request
    local_request = is_local_request(request)
    valid_token = validate_token(request)

    if not local_request and not valid_token:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # Check if the symbol exists in the volumes dictionary
    if symbol not in volumes:
        return jsonify({"status": "error", "message": f"Symbol '{symbol}' not found"}), 400

    # Convert time to minutes since midnight
    current_minutes = hour * 60 + minute

    # Calculate start time (5 minutes ago)
    start_minutes = current_minutes - 5

    # Initialize sum
    sum_volume = 0

    # Handle both normal case and midnight wrap-around
    if start_minutes >= 0:
        # Normal case - no midnight crossing
        for m in range(start_minutes, current_minutes):
            _hour = m // 60
            _min = m % 60
            sum_volume += volumes.get(symbol, {}).get(_hour, {}).get(_min, 0)
    else:
        # Midnight crossing - handle two segments
        # First segment: from start_minutes (negative) to midnight (1440 minutes)
        for m in range(start_minutes + 1440, 1440):
            _hour = m // 60
            _min = m % 60
            sum_volume += volumes.get(symbol, {}).get(_hour, {}).get(_min, 0)
        # Second segment: from midnight (0) to current_minutes
        for m in range(0, current_minutes):
            _hour = m // 60
            _min = m % 60
            sum_volume += volumes.get(symbol, {}).get(_hour, {}).get(_min, 0)

    return jsonify({
        "status": "success",
        "symbol": symbol,
        "volume": sum_volume
    }), 200


@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "OK"})


if __name__ == '__main__':
    # Run the server on port 5000 (or any other port you prefer)
    assemble_volume_dict()
    app.run(host='0.0.0.0', port=listen_port, debug=True)
