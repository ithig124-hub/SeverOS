import os, json, time
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
UPLOADS_DIR = os.path.join(DATA_DIR, 'dropshare_uploads')
MANIFEST_FILE = os.path.join(DATA_DIR, 'dropshare_manifest.json')

ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3',
    'zip', 'tar', 'gz', 'docx', 'xlsx', 'csv', 'json', 'md', 'py', 'js'
}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB

def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _load_manifest():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.isfile(MANIFEST_FILE):
        with open(MANIFEST_FILE) as f:
            return json.load(f)
    return []

def _save_manifest(m):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(m, f)

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/files', methods=['GET'])
    def list_files():
        manifest = _load_manifest()
        # Verify files still exist
        alive = [f for f in manifest if os.path.isfile(os.path.join(UPLOADS_DIR, f['stored_name']))]
        if len(alive) != len(manifest):
            _save_manifest(alive)
        return jsonify(alive)

    @bp.route('/api/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        f = request.files['file']
        if f.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        if not _allowed(f.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}'}), 400

        os.makedirs(UPLOADS_DIR, exist_ok=True)
        original_name = secure_filename(f.filename)
        timestamp = str(int(time.time()))
        stored_name = f"{timestamp}_{original_name}"
        dest_path = os.path.join(UPLOADS_DIR, stored_name)
        f.save(dest_path)
        size = os.path.getsize(dest_path)

        entry = {
            'id': timestamp,
            'original_name': original_name,
            'stored_name': stored_name,
            'size': size,
            'size_human': _human_size(size),
            'uploaded': time.strftime('%Y-%m-%d %H:%M:%S'),
            'ext': original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
        }
        manifest = _load_manifest()
        manifest.insert(0, entry)
        _save_manifest(manifest)
        return jsonify({'status': 'ok', 'file': entry})

    @bp.route('/api/files/<file_id>', methods=['DELETE'])
    def delete_file(file_id):
        manifest = _load_manifest()
        entry = next((f for f in manifest if f['id'] == file_id), None)
        if entry:
            try:
                os.remove(os.path.join(UPLOADS_DIR, entry['stored_name']))
            except OSError:
                pass
        manifest = [f for f in manifest if f['id'] != file_id]
        _save_manifest(manifest)
        return jsonify({'status': 'ok'})

    @bp.route('/api/download/<file_id>')
    def download_file(file_id):
        from flask import send_from_directory
        manifest = _load_manifest()
        entry = next((f for f in manifest if f['id'] == file_id), None)
        if not entry:
            return jsonify({'error': 'Not found'}), 404
        return send_from_directory(UPLOADS_DIR, entry['stored_name'], as_attachment=True, download_name=entry['original_name'])

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')

def _human_size(b):
    for unit in ['B','KB','MB','GB']:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"
