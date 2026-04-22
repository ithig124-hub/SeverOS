from flask import Blueprint, jsonify, request
import os

BASE = os.path.expanduser('~')

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/ls')
    def list_dir():
        path = request.args.get('path', BASE)
        # Safety: resolve and ensure within home
        real = os.path.realpath(path)
        if not real.startswith(os.path.realpath(BASE)):
            real = BASE
        items = []
        try:
            for entry in sorted(os.listdir(real)):
                full = os.path.join(real, entry)
                try:
                    stat = os.stat(full)
                    items.append({
                        'name': entry,
                        'is_dir': os.path.isdir(full),
                        'size': stat.st_size,
                        'path': full,
                    })
                except (PermissionError, OSError):
                    pass
        except (PermissionError, OSError):
            pass
        return jsonify({'path': real, 'items': items, 'parent': os.path.dirname(real)})

    @bp.route('/api/read')
    def read_file():
        path = request.args.get('path', '')
        real = os.path.realpath(path)
        if not real.startswith(os.path.realpath(BASE)):
            return jsonify({'error': 'Access denied'}), 403
        try:
            with open(real, 'r', errors='replace') as f:
                content = f.read(100000)
            return jsonify({'path': real, 'content': content})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
