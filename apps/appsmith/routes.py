import os, json, shutil
from flask import request, jsonify

def register(app, app_id):
    APPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    @app.route('/api/appsmith/create', methods=['POST'])
    def create_app():
        data = request.json
        name = data.get('name')
        emoji = data.get('icon', '📦')
        url = data.get('url')
        app_id = name.lower().replace(' ', '-')
        
        target_dir = os.path.join(APPS_DIR, app_id)
        if os.path.exists(target_dir):
            return jsonify({"error": "App already exists"}), 400
            
        os.makedirs(target_dir, exist_ok=True)
        
        manifest = {
            "id": app_id,
            "name": name,
            "icon": emoji,
            "description": f"Custom app created via App Smith",
            "category": "custom",
            "color": "#6366f1"
        }
        
        if url:
            manifest["external_url"] = url
            
        with open(os.path.join(target_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=4)
            
        if not url:
            templates_dir = os.path.join(APPS_DIR, '..', 'templates', 'apps')
            os.makedirs(templates_dir, exist_ok=True)
            with open(os.path.join(templates_dir, f'{app_id}.html'), 'w') as f:
                f.write('{% extends "app_base.html" %}\n{% block content %}\n<div class="glass-panel">\n    <h2>' + name + '</h2>\n    <p>Welcome to your new custom app!</p>\n</div>\n{% endblock %}')

        return jsonify({"status": "success", "app_id": app_id})