from flask import Blueprint, jsonify, request
import json, os

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'notes.json')

def _load():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def _save(notes):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(notes, f)

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/notes', methods=['GET'])
    def get_notes():
        return jsonify(_load())

    @bp.route('/api/notes', methods=['POST'])
    def save_note():
        data = request.get_json()
        notes = _load()
        existing = next((n for n in notes if n['id'] == data.get('id')), None)
        if existing:
            existing.update(data)
        else:
            notes.append(data)
        _save(notes)
        return jsonify({'status': 'ok'})

    @bp.route('/api/notes/<note_id>', methods=['DELETE'])
    def delete_note(note_id):
        notes = [n for n in _load() if n['id'] != note_id]
        _save(notes)
        return jsonify({'status': 'ok'})

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
