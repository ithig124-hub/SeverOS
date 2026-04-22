"""Alert System – Central notification hub with severity-based categorization."""

import time
import json
import os
from flask import Blueprint, jsonify, request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALERTS_FILE = os.path.join(BASE_DIR, 'data', 'alerts.json')


def _load_alerts():
    """Load alerts from disk."""
    if os.path.isfile(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return _default_alerts()


def _save_alerts(alerts):
    """Persist alerts to disk."""
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def _default_alerts():
    """Seed some example alerts."""
    now = time.time()
    return [
        {
            'id': 'a001',
            'severity': 'critical',
            'title': 'Disk Usage Above 90%',
            'message': 'Root partition is at 92% capacity. Consider cleaning up or expanding storage.',
            'source': 'System Monitor',
            'timestamp': now - 300,
            'read': False,
        },
        {
            'id': 'a002',
            'severity': 'warning',
            'title': 'High CPU Temperature',
            'message': 'CPU temperature reached 72°C. Ensure proper ventilation.',
            'source': 'System Monitor',
            'timestamp': now - 1800,
            'read': False,
        },
        {
            'id': 'a003',
            'severity': 'warning',
            'title': 'SSL Certificate Expiring',
            'message': 'Your SSL certificate expires in 14 days. Renew soon.',
            'source': 'Network Scanner',
            'timestamp': now - 7200,
            'read': True,
        },
        {
            'id': 'a004',
            'severity': 'info',
            'title': 'System Update Available',
            'message': 'ServerOS v2.1 is available with new features and security patches.',
            'source': 'Update Manager',
            'timestamp': now - 86400,
            'read': True,
        },
        {
            'id': 'a005',
            'severity': 'info',
            'title': 'Backup Completed',
            'message': 'Automated daily backup completed successfully at 03:00 AM.',
            'source': 'Backup Service',
            'timestamp': now - 43200,
            'read': True,
        },
        {
            'id': 'a006',
            'severity': 'critical',
            'title': 'Failed SSH Login Attempts',
            'message': '15 failed SSH login attempts detected from 203.0.113.42 in the last hour.',
            'source': 'Security Monitor',
            'timestamp': now - 600,
            'read': False,
        },
    ]


def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/alerts', methods=['GET'])
    def get_alerts():
        alerts = _load_alerts()
        severity = request.args.get('severity')
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        alerts.sort(key=lambda a: a['timestamp'], reverse=True)
        counts = {'critical': 0, 'warning': 0, 'info': 0, 'unread': 0}
        all_alerts = _load_alerts()
        for a in all_alerts:
            counts[a['severity']] = counts.get(a['severity'], 0) + 1
            if not a.get('read'):
                counts['unread'] += 1
        return jsonify({'alerts': alerts, 'counts': counts})

    @bp.route('/api/alerts/create', methods=['POST'])
    def create_alert():
        data = request.get_json() or {}
        severity = data.get('severity', 'info')
        if severity not in ('info', 'warning', 'critical'):
            return jsonify({'error': 'Invalid severity. Use info, warning, or critical.'}), 400
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Title is required.'}), 400
        alerts = _load_alerts()
        new_alert = {
            'id': f"a{int(time.time() * 1000)}",
            'severity': severity,
            'title': title,
            'message': data.get('message', '').strip(),
            'source': data.get('source', 'Manual'),
            'timestamp': time.time(),
            'read': False,
        }
        alerts.insert(0, new_alert)
        _save_alerts(alerts)
        return jsonify({'status': 'created', 'alert': new_alert}), 201

    @bp.route('/api/alerts/clear', methods=['POST'])
    def clear_alerts():
        data = request.get_json() or {}
        mode = data.get('mode', 'read')  # 'read' = mark all read, 'all' = delete all, 'id' = clear by id
        alerts = _load_alerts()
        if mode == 'all':
            alerts = []
        elif mode == 'id':
            alert_id = data.get('id', '')
            alerts = [a for a in alerts if a['id'] != alert_id]
        else:  # mark all as read
            for a in alerts:
                a['read'] = True
        _save_alerts(alerts)
        return jsonify({'status': 'cleared', 'mode': mode, 'remaining': len(alerts)})

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
