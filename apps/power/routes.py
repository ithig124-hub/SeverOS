import os, subprocess
from flask import request, jsonify

def register(app, app_id):
    @app.route('/api/power/reboot', methods=['POST'])
    def reboot():
        os.system('sudo reboot')
        return jsonify({"status": "Rebooting..."})

    @app.route('/api/power/shutdown', methods=['POST'])
    def shutdown():
        os.system('sudo shutdown now')
        return jsonify({"status": "Shutting down..."})

    @app.route('/api/power/update', methods=['POST'])
    def update_system():
        try:
            subprocess.run(['git', 'pull'], check=True)
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
            return jsonify({"status": "System updated. Please restart ServerOS or Reboot Pi."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500