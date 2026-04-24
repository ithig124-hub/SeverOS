import os
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