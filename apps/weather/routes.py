import requests
from flask import jsonify
def register(app, app_id):
    @app.route('/api/weather/forecast')
    def get_weather():
        lat, lon = 51.5074, -0.1278
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
            res = requests.get(url).json()
            return jsonify(res)
        except Exception as e: return jsonify({"error": str(e)})