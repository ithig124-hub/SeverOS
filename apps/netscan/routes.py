import subprocess
from flask import jsonify

def register(app, app_id):
    @app.route('/api/netscan/devices')
    def get_devices():
        try:
            output = subprocess.check_output(['ip', 'neighbor', 'show']).decode('utf-8')
            devices = []
            for line in output.split('\n'):
                if 'REACHABLE' in line or 'STALE' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        devices.append({"ip": parts[0], "mac": parts[4], "state": parts[-1]})
            return jsonify(devices)
        except Exception as e:
            return jsonify({"error": str(e)})