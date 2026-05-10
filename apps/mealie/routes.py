import os, json
from flask import Blueprint, jsonify, request

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'recipes.json')

def _load():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def _save(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/recipes', methods=['GET'])
    def get_recipes():
        return jsonify(_load())

    @bp.route('/api/recipes', methods=['POST'])
    def save_recipe():
        recipe = request.get_json()
        recipes = _load()
        existing = next((r for r in recipes if r.get('id') == recipe.get('id')), None)
        if existing:
            existing.update(recipe)
        else:
            recipes.append(recipe)
        _save(recipes)
        return jsonify({'status': 'ok'})

    @bp.route('/api/recipes/<recipe_id>', methods=['DELETE'])
    def delete_recipe(recipe_id):
        recipes = [r for r in _load() if r.get('id') != recipe_id]
        _save(recipes)
        return jsonify({'status': 'ok'})

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
