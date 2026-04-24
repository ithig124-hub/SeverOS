import os, json, time, subprocess
from flask import jsonify
def register(app, app_id):
    DATA_FILE = os.path.join('data', 'speedtest.json')
    def load_history():
        if not os.path.exists(DATA_FILE): return []
        try:
            with open(DATA_FILE, 'r') as f: return json.load(f)
        except: return []
    @app.route('/api/speedtest/run', methods=['POST'])
    def run_test():
        try:
            output = subprocess.check_output(['speedtest-cli', '--json']).decode('utf-8')
            data = json.loads(output)
            result = {"timestamp": time.time(), "download": round(data['download']/1_000_000, 2), "upload": round(data['upload']/1_000_000, 2), "ping": round(data['ping'], 1)}
            history = load_history()
            history.append(result)
            if len(history) > 24: history.pop(0)
            with open(DATA_FILE, 'w') as f: json.dump(history, f)
            return jsonify(result)
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/speedtest/history')
    def get_history(): return jsonify(load_history())