"""Tests for ServerOS Pro Suite – Multi-Dashboard, Alerts, Automation, Network."""

import json
import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, discover_apps, get_apps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

@pytest.fixture(autouse=True)
def clean_data_files():
    """Remove test data files before/after each test."""
    files_to_clean = [
        os.path.join(BASE_DIR, 'data', 'alerts.json'),
        os.path.join(BASE_DIR, 'data', 'automation_rules.json'),
        os.path.join(BASE_DIR, 'data', 'network_chat.json'),
        os.path.join(BASE_DIR, 'data', 'network_broadcasts.json'),
    ]
    for f in files_to_clean:
        if os.path.isfile(f):
            os.remove(f)
    yield
    for f in files_to_clean:
        if os.path.isfile(f):
            os.remove(f)


# ═══════ PRO SUITE APP DISCOVERY ═══════

def test_pro_suite_apps_discovered():
    discover_apps()
    apps = get_apps()
    pro_apps = {'multi-dashboard', 'alerts', 'automation', 'network'}
    for app_id in pro_apps:
        assert app_id in apps, f"Pro Suite app '{app_id}' not discovered"

def test_pro_suite_manifests_valid():
    discover_apps()
    pro_apps = {'multi-dashboard': 'pro-suite', 'alerts': 'pro-suite',
                'automation': 'pro-suite', 'network': 'pro-suite'}
    for app_id, category in pro_apps.items():
        manifest = get_apps()[app_id]
        assert manifest['category'] == category
        assert manifest['icon']
        assert manifest['description']
        assert manifest['color'].startswith('#')

def test_pro_suite_pages_load(client):
    for app_id in ['multi-dashboard', 'alerts', 'automation', 'network']:
        resp = client.get(f'/app/{app_id}')
        assert resp.status_code == 200, f"/app/{app_id} returned {resp.status_code}"
        html = resp.data.decode()
        assert '← Dashboard' in html
        assert 'glass' in html.lower() or 'var(--glass' in html


# ═══════ MULTI-SOURCE DASHBOARD ═══════

class TestMultiDashboard:
    def test_weather_api(self, client):
        resp = client.get('/app/multi-dashboard/api/dashboard/weather')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'location' in data
        assert 'temperature_c' in data
        assert 'temperature_f' in data
        assert 'condition' in data
        assert 'humidity' in data
        assert 'forecast' in data
        assert isinstance(data['forecast'], list)
        assert len(data['forecast']) >= 3
        for f in data['forecast']:
            assert 'day' in f
            assert 'high_c' in f
            assert 'icon' in f

    def test_stocks_api(self, client):
        resp = client.get('/app/multi-dashboard/api/dashboard/stocks')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tickers' in data
        assert 'indices' in data
        assert 'market_status' in data
        assert len(data['tickers']) >= 4
        for t in data['tickers']:
            assert 'symbol' in t
            assert 'price' in t
            assert 'change' in t
            assert 'change_pct' in t
        for i in data['indices']:
            assert 'name' in i
            assert 'value' in i

    def test_network_api(self, client):
        resp = client.get('/app/multi-dashboard/api/dashboard/network')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'bytes_sent' in data
        assert 'bytes_recv' in data
        assert 'interfaces' in data
        assert 'active_connections' in data
        assert isinstance(data['interfaces'], dict)

    def test_system_api(self, client):
        resp = client.get('/app/multi-dashboard/api/dashboard/system')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'cpu_percent' in data
        assert 'ram_percent' in data
        assert 'disk_percent' in data
        assert 'uptime' in data
        assert isinstance(data['cpu_percent'], (int, float))

    def test_weather_caching(self, client):
        """Second call should return cached data with same timestamp."""
        resp1 = client.get('/app/multi-dashboard/api/dashboard/weather')
        data1 = resp1.get_json()
        resp2 = client.get('/app/multi-dashboard/api/dashboard/weather')
        data2 = resp2.get_json()
        assert data1['last_updated'] == data2['last_updated']

    def test_stocks_caching(self, client):
        resp1 = client.get('/app/multi-dashboard/api/dashboard/stocks')
        data1 = resp1.get_json()
        resp2 = client.get('/app/multi-dashboard/api/dashboard/stocks')
        data2 = resp2.get_json()
        assert data1['last_updated'] == data2['last_updated']


# ═══════ ALERT SYSTEM ═══════

class TestAlertSystem:
    def test_get_alerts_returns_defaults(self, client):
        resp = client.get('/app/alerts/api/alerts')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'alerts' in data
        assert 'counts' in data
        assert len(data['alerts']) >= 4
        assert data['counts']['critical'] >= 1
        assert data['counts']['warning'] >= 1

    def test_get_alerts_filter_by_severity(self, client):
        resp = client.get('/app/alerts/api/alerts?severity=critical')
        data = resp.get_json()
        for a in data['alerts']:
            assert a['severity'] == 'critical'

    def test_create_alert(self, client):
        payload = {
            'severity': 'warning',
            'title': 'Test Alert',
            'message': 'Something happened',
            'source': 'Test Suite'
        }
        resp = client.post('/app/alerts/api/alerts/create',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'created'
        assert data['alert']['title'] == 'Test Alert'
        assert data['alert']['severity'] == 'warning'
        assert 'id' in data['alert']

    def test_create_alert_missing_title(self, client):
        resp = client.post('/app/alerts/api/alerts/create',
                           data=json.dumps({'severity': 'info'}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_create_alert_invalid_severity(self, client):
        resp = client.post('/app/alerts/api/alerts/create',
                           data=json.dumps({'severity': 'bogus', 'title': 'Test'}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_clear_alerts_mark_read(self, client):
        resp = client.post('/app/alerts/api/alerts/clear',
                           data=json.dumps({'mode': 'read'}),
                           content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'cleared'
        # Verify all are read now
        resp2 = client.get('/app/alerts/api/alerts')
        data2 = resp2.get_json()
        assert data2['counts']['unread'] == 0

    def test_clear_alerts_delete_all(self, client):
        resp = client.post('/app/alerts/api/alerts/clear',
                           data=json.dumps({'mode': 'all'}),
                           content_type='application/json')
        assert resp.status_code == 200
        resp2 = client.get('/app/alerts/api/alerts')
        assert len(resp2.get_json()['alerts']) == 0

    def test_clear_alerts_by_id(self, client):
        # Get the first alert ID
        resp = client.get('/app/alerts/api/alerts')
        alerts = resp.get_json()['alerts']
        target_id = alerts[0]['id']
        count_before = len(alerts)
        # Clear it
        resp = client.post('/app/alerts/api/alerts/clear',
                           data=json.dumps({'mode': 'id', 'id': target_id}),
                           content_type='application/json')
        assert resp.status_code == 200
        resp2 = client.get('/app/alerts/api/alerts')
        count_after = len(resp2.get_json()['alerts'])
        assert count_after == count_before - 1

    def test_alert_has_required_fields(self, client):
        resp = client.get('/app/alerts/api/alerts')
        for a in resp.get_json()['alerts']:
            assert 'id' in a
            assert 'severity' in a
            assert a['severity'] in ('info', 'warning', 'critical')
            assert 'title' in a
            assert 'timestamp' in a
            assert 'read' in a


# ═══════ AUTOMATION ENGINE ═══════

class TestAutomationEngine:
    def test_get_rules_returns_defaults(self, client):
        resp = client.get('/app/automation/api/rules')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'rules' in data
        assert 'total' in data
        assert 'enabled' in data
        assert data['total'] >= 3

    def test_create_rule(self, client):
        payload = {
            'name': 'Test Rule',
            'trigger': {'type': 'cpu_percent', 'operator': '>', 'value': 95},
            'action': {'type': 'alert', 'value': 'CPU is very high!'}
        }
        resp = client.post('/app/automation/api/rules',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'created'
        assert data['rule']['name'] == 'Test Rule'
        assert data['rule']['enabled'] is True

    def test_create_rule_missing_name(self, client):
        resp = client.post('/app/automation/api/rules',
                           data=json.dumps({'trigger': {'type': 'time'}, 'action': {'type': 'theme'}}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_create_rule_missing_trigger_type(self, client):
        resp = client.post('/app/automation/api/rules',
                           data=json.dumps({'name': 'Bad', 'trigger': {}, 'action': {'type': 'theme'}}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_update_rule(self, client):
        # Get existing rule ID
        resp = client.get('/app/automation/api/rules')
        rule_id = resp.get_json()['rules'][0]['id']
        # Update it
        resp = client.put(f'/app/automation/api/rules/{rule_id}',
                          data=json.dumps({'enabled': False}),
                          content_type='application/json')
        assert resp.status_code == 200
        assert resp.get_json()['rule']['enabled'] is False

    def test_update_nonexistent_rule(self, client):
        resp = client.put('/app/automation/api/rules/nonexistent',
                          data=json.dumps({'enabled': False}),
                          content_type='application/json')
        assert resp.status_code == 404

    def test_delete_rule(self, client):
        resp = client.get('/app/automation/api/rules')
        rule_id = resp.get_json()['rules'][0]['id']
        count_before = resp.get_json()['total']
        resp = client.delete(f'/app/automation/api/rules/{rule_id}')
        assert resp.status_code == 200
        resp2 = client.get('/app/automation/api/rules')
        assert resp2.get_json()['total'] == count_before - 1

    def test_delete_nonexistent_rule(self, client):
        resp = client.delete('/app/automation/api/rules/nonexistent')
        assert resp.status_code == 404

    def test_evaluate_rules(self, client):
        resp = client.get('/app/automation/api/rules/evaluate')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'evaluated' in data
        assert 'triggered' in data
        assert 'results' in data
        assert isinstance(data['results'], list)

    def test_rule_schema(self, client):
        resp = client.get('/app/automation/api/rules/schema')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'trigger_types' in data
        assert 'action_types' in data
        trigger_types = {t['type'] for t in data['trigger_types']}
        assert 'time' in trigger_types
        assert 'cpu_percent' in trigger_types
        action_types = {a['type'] for a in data['action_types']}
        assert 'theme' in action_types
        assert 'alert' in action_types


# ═══════ NETWORK & COMMUNICATION ═══════

class TestNetwork:
    def test_get_chat_returns_defaults(self, client):
        resp = client.get('/app/network/api/chat')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'messages' in data
        assert len(data['messages']) >= 2

    def test_send_chat_message(self, client):
        payload = {'text': 'Hello from test!', 'sender': 'TestBot'}
        resp = client.post('/app/network/api/chat',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'sent'
        assert data['message']['text'] == 'Hello from test!'
        # Verify it's in the list now
        resp2 = client.get('/app/network/api/chat')
        texts = [m['text'] for m in resp2.get_json()['messages']]
        assert 'Hello from test!' in texts

    def test_send_chat_empty_text(self, client):
        resp = client.post('/app/network/api/chat',
                           data=json.dumps({'text': '  ', 'sender': 'Test'}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_network_scan(self, client):
        resp = client.get('/app/network/api/network/scan')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'devices' in data
        assert 'local_ip' in data
        assert 'subnet' in data
        assert 'total_online' in data
        assert len(data['devices']) >= 5
        for d in data['devices']:
            assert 'ip' in d
            assert 'hostname' in d
            assert 'mac' in d
            assert 'status' in d
            assert d['status'] in ('online', 'offline')

    def test_get_broadcasts(self, client):
        resp = client.get('/app/network/api/network/broadcast')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'broadcasts' in data

    def test_create_broadcast(self, client):
        payload = {'filename': 'test.pdf', 'url': '/files/test.pdf', 'size_bytes': 1024}
        resp = client.post('/app/network/api/network/broadcast',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'broadcast_sent'
        assert data['broadcast']['filename'] == 'test.pdf'

    def test_create_broadcast_missing_fields(self, client):
        resp = client.post('/app/network/api/network/broadcast',
                           data=json.dumps({'filename': 'test.pdf'}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_chat_since_filter(self, client):
        # Send a new message
        client.post('/app/network/api/chat',
                    data=json.dumps({'text': 'Recent msg', 'sender': 'Test'}),
                    content_type='application/json')
        # Filter with a very recent timestamp
        future_ts = time.time() + 10
        resp = client.get(f'/app/network/api/chat?since={future_ts}')
        data = resp.get_json()
        assert len(data['messages']) == 0


# ═══════ INTEGRATION TESTS ═══════

class TestProSuiteIntegration:
    def test_pro_suite_apps_on_main_dashboard(self, client):
        """All pro suite apps appear on the main dashboard."""
        resp = client.get('/')
        html = resp.data.decode()
        assert 'multi-dashboard' in html
        assert 'alerts' in html
        assert 'automation' in html
        assert 'network' in html

    def test_pro_suite_in_api_apps(self, client):
        resp = client.get('/api/apps')
        ids = {a['id'] for a in resp.get_json()}
        assert 'multi-dashboard' in ids
        assert 'alerts' in ids
        assert 'automation' in ids
        assert 'network' in ids

    def test_all_pro_suite_use_glassmorphism(self, client):
        """All pro suite templates include glassmorphism CSS variables."""
        for app_id in ['multi-dashboard', 'alerts', 'automation', 'network']:
            resp = client.get(f'/app/{app_id}')
            html = resp.data.decode()
            assert 'var(--glass' in html or 'glass-bg' in html, \
                f"{app_id} missing glassmorphism styling"
