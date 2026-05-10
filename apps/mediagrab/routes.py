import os, json, subprocess, re
from flask import Blueprint, jsonify, request

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
DOWNLOADS_FILE = os.path.join(DATA_DIR, 'mediagrab_history.json')

def _load_history():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.isfile(DOWNLOADS_FILE):
        with open(DOWNLOADS_FILE) as f:
            return json.load(f)
    return []

def _save_history(h):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DOWNLOADS_FILE, 'w') as f:
        json.dump(h, f)

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/history')
    def history():
        return jsonify(_load_history())

    @bp.route('/api/grab', methods=['POST'])
    def grab():
        data = request.get_json()
        url = data.get('url', '').strip()
        fmt = data.get('format', 'mp4')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Try to get title via yt-dlp if available, else mock
        title = url
        try:
            out = subprocess.check_output(
                ['yt-dlp', '--get-title', url],
                timeout=10, stderr=subprocess.DEVNULL
            ).decode().strip()
            if out:
                title = out
        except Exception:
            # yt-dlp not installed — record as pending
            title = re.sub(r'https?://(www\.)?', '', url)[:60]

        entry = {
            'id': str(__import__('time').time()),
            'url': url,
            'title': title,
            'format': fmt,
            'status': 'queued',
            'added': __import__('time').strftime('%Y-%m-%d %H:%M:%S')
        }
        history = _load_history()
        history.insert(0, entry)
        if len(history) > 50:
            history = history[:50]
        _save_history(history)
        return jsonify({'status': 'queued', 'entry': entry})

    @bp.route('/api/history/<entry_id>', methods=['DELETE'])
    def delete_entry(entry_id):
        history = [e for e in _load_history() if e.get('id') != entry_id]
        _save_history(history)
        return jsonify({'status': 'ok'})

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
