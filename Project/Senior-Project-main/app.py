import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyBvhCXdJ2pRT86oQbh5QaFS-BUCg3Aa9Qk"

@app.route('/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    url = f"https://weather.googleapis.com/v1/history/hours:lookup"
    params = {
        "key": GOOGLE_API_KEY,
        "location.latitude": lat,
        "location.longitude": lon,
        "hours": 8,
        "pageSize": 5
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch weather"}), response.status_code
