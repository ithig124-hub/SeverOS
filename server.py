#!/usr/bin/env python3
"""
ServerOS - A lightweight, modular dashboard server
Inspired by Umbrel, built for Raspberry Pi Zero 2 W
Auto-discovers and registers apps from the /apps/ directory.
"""

import os
import json
import importlib.util
from flask import Flask, render_template, jsonify, send_from_directory, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(BASE_DIR, 'apps')

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['SECRET_KEY'] = os.urandom(24).hex()

# ── App Registry ──────────────────────────────────────────────
_registry = {}

def discover_apps():
    """Scan /apps/ for manifest.json and register each app."""
    _registry.clear()
    if not os.path.isdir(APPS_DIR):
        return
    for entry in sorted(os.listdir(APPS_DIR)):
        app_path = os.path.join(APPS_DIR, entry)
        manifest_path = os.path.join(app_path, 'manifest.json')
        if os.path.isdir(app_path) and os.path.isfile(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                manifest.setdefault('id', entry)
                manifest.setdefault('name', entry.title())
                manifest.setdefault('icon', '📦')
                manifest.setdefault('description', '')
                manifest.setdefault('category', 'utility')
                manifest.setdefault('color', '#667eea')
                _registry[entry] = manifest

                # Load routes.py if present
                routes_path = os.path.join(app_path, 'routes.py')
                if os.path.isfile(routes_path):
                    spec = importlib.util.spec_from_file_location(
                        f"apps.{entry}.routes", routes_path
                    )
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, 'register'):
                        mod.register(app, entry)
            except Exception as e:
                print(f"[ServerOS] Warning: Failed to load app '{entry}': {e}")

def get_apps():
    return _registry

# ── Core Routes ───────────────────────────────────────────────
@app.route('/')
def index():
    apps_list = []
    for app_id, manifest in get_apps().items():
        apps_list.append({
            'id': app_id,
            'name': manifest.get('name', app_id),
            'icon': manifest.get('icon', '📦'),
            'description': manifest.get('description', ''),
            'category': manifest.get('category', 'utility'),
            'color': manifest.get('color', '#667eea'),
            'url': f'/app/{app_id}'
        })
    return render_template('dashboard.html', apps=apps_list)

@app.route('/api/apps')
def api_apps():
    apps_list = []
    for app_id, manifest in get_apps().items():
        apps_list.append({
            'id': app_id,
            'name': manifest.get('name', app_id),
            'icon': manifest.get('icon', '📦'),
            'description': manifest.get('description', ''),
            'category': manifest.get('category', 'utility'),
            'color': manifest.get('color', '#667eea'),
            'url': f'/app/{app_id}'
        })
    return jsonify(apps_list)

@app.route('/api/stats')
def api_stats():
    """Return real system stats using psutil."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        temps = {}
        try:
            t = psutil.sensors_temperatures()
            for name, entries in t.items():
                for e in entries:
                    temps[e.label or name] = round(e.current, 1)
        except Exception:
            temps = {"cpu": "N/A"}
        boot = psutil.boot_time()
        import time
        uptime_sec = int(time.time() - boot)
        hours, remainder = divmod(uptime_sec, 3600)
        minutes, secs = divmod(remainder, 60)
        return jsonify({
            'cpu_percent': cpu,
            'ram_total_gb': round(mem.total / (1024**3), 2),
            'ram_used_gb': round(mem.used / (1024**3), 2),
            'ram_percent': mem.percent,
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_used_gb': round(disk.used / (1024**3), 2),
            'disk_percent': disk.percent,
            'temperatures': temps,
            'uptime': f"{hours}h {minutes}m {secs}s",
            'cpu_count': psutil.cpu_count(),
            'net_io': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
            }
        })
    except ImportError:
        return jsonify({'error': 'psutil not installed. Run setup.sh'}), 500

@app.route('/api/widget/stats')
def api_widget_stats():
    """Compact widget data for the dashboard header chips and storage card."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Aggregate all mounted storage
        total_storage_bytes = 0
        used_storage_bytes = 0
        try:
            from core.storage_manager import get_disk_health
            disks = get_disk_health()
            for d in disks:
                total_storage_bytes += d.get('total_bytes', 0)
                used_storage_bytes += d.get('used_bytes', 0)
        except Exception:
            total_storage_bytes = disk.total
            used_storage_bytes = disk.used

        total_tb = round(total_storage_bytes / (1024**4), 2)
        used_tb = round(used_storage_bytes / (1024**4), 2)
        storage_pct = round(used_storage_bytes / total_storage_bytes * 100, 1) if total_storage_bytes else 0

        return jsonify({
            'cpu_percent': cpu,
            'ram_percent': mem.percent,
            'ram_used_gb': round(mem.used / (1024**3), 2),
            'ram_total_gb': round(mem.total / (1024**3), 2),
            'disk_percent': disk.percent,
            'storage_used_tb': used_tb,
            'storage_total_tb': total_tb,
            'storage_percent': storage_pct,
        })
    except ImportError:
        return jsonify({'error': 'psutil not installed'}), 500

@app.route('/api/wallpaper', methods=['GET', 'POST'])
def api_wallpaper():
    """Get or set the dashboard wallpaper."""
    wp_file = os.path.join(BASE_DIR, 'data', 'wallpaper.json')
    os.makedirs(os.path.dirname(wp_file), exist_ok=True)
    if request.method == 'POST':
        data = request.get_json()
        with open(wp_file, 'w') as f:
            json.dump(data, f)
        return jsonify({'status': 'ok'})
    else:
        if os.path.isfile(wp_file):
            with open(wp_file) as f:
                return jsonify(json.load(f))
        return jsonify({'type': 'gradient', 'value': 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)'})

@app.route('/api/storage/drives')
def api_storage_drives():
    """List external/removable USB drives."""
    from core.storage_manager import get_external_drives
    return jsonify(get_external_drives())

@app.route('/api/storage/health')
def api_storage_health():
    """Disk health and usage for all mounted filesystems."""
    from core.storage_manager import get_disk_health
    return jsonify(get_disk_health())

@app.route('/api/storage/mount', methods=['POST'])
def api_storage_mount():
    """Mount an external drive partition."""
    from core.storage_manager import mount_drive
    data = request.get_json() or {}
    device = data.get('device', '')
    mount_point = data.get('mount_point')
    if not device:
        return jsonify({'success': False, 'message': 'No device specified'}), 400
    success, message = mount_drive(device, mount_point)
    return jsonify({'success': success, 'message': message})

@app.route('/api/storage/unmount', methods=['POST'])
def api_storage_unmount():
    """Unmount a drive."""
    from core.storage_manager import unmount_drive
    data = request.get_json() or {}
    mount_point = data.get('mount_point', '')
    if not mount_point:
        return jsonify({'success': False, 'message': 'No mount point specified'}), 400
    success, message = unmount_drive(mount_point)
    return jsonify({'success': success, 'message': message})

@app.route('/app/<app_id>')
def app_page(app_id):
    if app_id not in _registry:
        return "App not found", 404
    manifest = _registry[app_id]
    template = f"apps/{app_id}.html"
    try:
        return render_template(template, manifest=manifest, app_id=app_id)
    except Exception:
        index_path = os.path.join(APPS_DIR, app_id, 'templates', 'index.html')
        if os.path.isfile(index_path):
            with open(index_path) as f:
                return f.read()
        return f"App '{app_id}' template not found", 404

@app.route('/apps/<app_id>/static/<path:filename>')
def app_static(app_id, filename):
    static_dir = os.path.join(APPS_DIR, app_id, 'static')
    return send_from_directory(static_dir, filename)

# ── Init ──────────────────────────────────────────────────────
with app.app_context():
    discover_apps()

if __name__ == '__main__':
    print(f"\n🖥️  ServerOS starting...")
    print(f"   Found {len(_registry)} apps: {', '.join(_registry.keys())}")
    print(f"   Dashboard: http://0.0.0.0:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
