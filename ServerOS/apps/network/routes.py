"""Network & Communication – Local chat, network scanner, file broadcast."""

import time
import json
import os
from flask import Blueprint, jsonify, request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_FILE = os.path.join(BASE_DIR, 'data', 'network_chat.json')
BROADCASTS_FILE = os.path.join(BASE_DIR, 'data', 'network_broadcasts.json')


def _load_json(filepath, default=None):
    if default is None:
        default = []
    if os.path.isfile(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default


def _save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    # ── Local Chat ──
    @bp.route('/api/chat', methods=['GET'])
    def get_chat():
        messages = _load_json(CHAT_FILE, _default_chat())
        since = request.args.get('since')
        if since:
            try:
                since_ts = float(since)
                messages = [m for m in messages if m['timestamp'] > since_ts]
            except ValueError:
                pass
        return jsonify({'messages': messages[-100:], 'total': len(messages)})

    @bp.route('/api/chat', methods=['POST'])
    def send_chat():
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Message text is required.'}), 400
        sender = data.get('sender', 'Anonymous')
        device = data.get('device', request.remote_addr or 'unknown')
        messages = _load_json(CHAT_FILE, [])
        msg = {
            'id': f"m{int(time.time() * 1000)}",
            'sender': sender[:30],
            'device': device[:50],
            'text': text[:500],
            'timestamp': time.time(),
        }
        messages.append(msg)
        # Keep last 500 messages
        if len(messages) > 500:
            messages = messages[-500:]
        _save_json(CHAT_FILE, messages)
        return jsonify({'status': 'sent', 'message': msg}), 201

    # ── Network Scanner (mock) ──
    @bp.route('/api/network/scan', methods=['GET'])
    def network_scan():
        try:
            import psutil
            addrs = {}
            for iface, addr_list in psutil.net_if_addrs().items():
                for addr in addr_list:
                    if addr.family == 2:
                        addrs[iface] = addr.address
            local_ip = list(addrs.values())[0] if addrs else '192.168.1.100'
        except ImportError:
            local_ip = '192.168.1.100'
            addrs = {'eth0': '192.168.1.100'}

        prefix = '.'.join(local_ip.split('.')[:3])
        devices = [
            {'ip': f'{prefix}.1', 'hostname': 'router.local', 'mac': 'AA:BB:CC:DD:EE:01', 'type': 'router', 'status': 'online', 'latency_ms': 1.2},
            {'ip': f'{prefix}.10', 'hostname': 'nas-server.local', 'mac': 'AA:BB:CC:DD:EE:10', 'type': 'server', 'status': 'online', 'latency_ms': 2.1},
            {'ip': f'{prefix}.20', 'hostname': 'macbook-pro.local', 'mac': 'AA:BB:CC:DD:EE:20', 'type': 'laptop', 'status': 'online', 'latency_ms': 3.5},
            {'ip': f'{prefix}.21', 'hostname': 'iphone-14.local', 'mac': 'AA:BB:CC:DD:EE:21', 'type': 'phone', 'status': 'online', 'latency_ms': 8.2},
            {'ip': f'{prefix}.30', 'hostname': 'pi-zero-2w.local', 'mac': 'AA:BB:CC:DD:EE:30', 'type': 'sbc', 'status': 'online', 'latency_ms': 1.8},
            {'ip': f'{prefix}.40', 'hostname': 'smart-tv.local', 'mac': 'AA:BB:CC:DD:EE:40', 'type': 'media', 'status': 'online', 'latency_ms': 5.0},
            {'ip': f'{prefix}.50', 'hostname': 'printer.local', 'mac': 'AA:BB:CC:DD:EE:50', 'type': 'printer', 'status': 'offline', 'latency_ms': None},
            {'ip': f'{prefix}.60', 'hostname': 'smart-speaker.local', 'mac': 'AA:BB:CC:DD:EE:60', 'type': 'iot', 'status': 'online', 'latency_ms': 12.4},
        ]
        return jsonify({
            'local_ip': local_ip,
            'interfaces': addrs,
            'subnet': f'{prefix}.0/24',
            'devices': devices,
            'total_online': sum(1 for d in devices if d['status'] == 'online'),
            'total_offline': sum(1 for d in devices if d['status'] == 'offline'),
            'scan_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        })

    # ── File Broadcast ──
    @bp.route('/api/network/broadcast', methods=['GET'])
    def get_broadcasts():
        broadcasts = _load_json(BROADCASTS_FILE, _default_broadcasts())
        return jsonify({'broadcasts': broadcasts[-50:]})

    @bp.route('/api/network/broadcast', methods=['POST'])
    def create_broadcast():
        data = request.get_json() or {}
        filename = data.get('filename', '').strip()
        url = data.get('url', '').strip()
        if not filename or not url:
            return jsonify({'error': 'filename and url are required.'}), 400
        broadcasts = _load_json(BROADCASTS_FILE, [])
        entry = {
            'id': f"b{int(time.time() * 1000)}",
            'filename': filename[:100],
            'url': url[:500],
            'sender': data.get('sender', request.remote_addr or 'unknown'),
            'size_bytes': data.get('size_bytes', 0),
            'timestamp': time.time(),
        }
        broadcasts.append(entry)
        if len(broadcasts) > 100:
            broadcasts = broadcasts[-100:]
        _save_json(BROADCASTS_FILE, broadcasts)
        return jsonify({'status': 'broadcast_sent', 'broadcast': entry}), 201

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')


def _default_chat():
    now = time.time()
    return [
        {'id': 'm001', 'sender': 'ServerOS', 'device': 'pi-zero-2w.local', 'text': 'Welcome to the local network chat! 🎉', 'timestamp': now - 3600},
        {'id': 'm002', 'sender': 'NAS Server', 'device': 'nas-server.local', 'text': 'Backup completed successfully.', 'timestamp': now - 1800},
        {'id': 'm003', 'sender': 'Admin', 'device': 'macbook-pro.local', 'text': 'Running maintenance window at 3 AM tonight.', 'timestamp': now - 600},
    ]


def _default_broadcasts():
    now = time.time()
    return [
        {'id': 'b001', 'filename': 'server-logs-2024.tar.gz', 'url': '/files/server-logs-2024.tar.gz', 'sender': 'pi-zero-2w.local', 'size_bytes': 15728640, 'timestamp': now - 7200},
        {'id': 'b002', 'filename': 'config-backup.zip', 'url': '/files/config-backup.zip', 'sender': 'nas-server.local', 'size_bytes': 2097152, 'timestamp': now - 3600},
    ]
