import os, json
from flask import request, jsonify

def register(app, app_id):
    DATA_FILE = os.path.join('data', 'grocery.json')
    def load_list():
        if not os.path.exists(DATA_FILE): return []
        try:
            with open(DATA_FILE, 'r') as f: return json.load(f)
        except: return []
    @app.route('/api/grocery', methods=['GET', 'POST', 'DELETE'])
    def handle_grocery():
        items = load_list()
        if request.method == 'POST':
            items.append(request.json)
            with open(DATA_FILE, 'w') as f: json.dump(items, f)
            return jsonify({"status": "success"})
        if request.method == 'DELETE':
            with open(DATA_FILE, 'w') as f: json.dump([], f)
            return jsonify({"status": "cleared"})
        return jsonify(items)
    @app.route('/api/grocery/toggle', methods=['POST'])
    def toggle_item():
        items = load_list()
        idx = request.json.get('index')
        if 0 <= idx < len(items):
            items[idx]['checked'] = not items[idx]['checked']
            with open(DATA_FILE, 'w') as f: json.dump(items, f)
        return jsonify(items)