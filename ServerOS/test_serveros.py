"""Tests for ServerOS – server, app discovery, routes, and API endpoints."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, discover_apps, get_apps

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

# ── App Discovery ──

def test_discover_finds_all_16_apps():
    discover_apps()
    apps = get_apps()
    expected = {'globe','snackscout','library','map','search','notes',
                'dashboard','tracking','wallpaper','worldclock','monitor','filemanager',
                'multi-dashboard','alerts','automation','network'}
    assert set(apps.keys()) == expected, f"Missing apps: {expected - set(apps.keys())}"

def test_manifests_have_required_fields():
    discover_apps()
    for app_id, manifest in get_apps().items():
        assert 'name' in manifest, f"{app_id} missing name"
        assert 'icon' in manifest, f"{app_id} missing icon"
        assert 'description' in manifest, f"{app_id} missing description"
        assert 'color' in manifest, f"{app_id} missing color"

# ── Dashboard ──

def test_dashboard_loads(client):
    resp = client.get('/')
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'ServerOS' in html
    assert 'app-grid' in html

def test_dashboard_lists_all_apps(client):
    resp = client.get('/')
    html = resp.data.decode()
    for name in ['3D Globe','SnackScout','Library','Map Explorer','Universal Search',
                 'Notes','Smart Dashboard','GPS Tracker','Wallpaper Manager',
                 'World Clock','System Monitor','File Manager',
                 'Multi-Source Dashboard','Alert System','Automation Engine','Network &amp; Comms']:
        assert name in html, f"Dashboard missing app: {name}"

# ── API ──

def test_api_apps_returns_json(client):
    resp = client.get('/api/apps')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 16
    ids = {a['id'] for a in data}
    assert 'globe' in ids
    assert 'wallpaper' in ids
    assert 'worldclock' in ids
    assert 'multi-dashboard' in ids
    assert 'alerts' in ids
    assert 'automation' in ids
    assert 'network' in ids

def test_api_stats_returns_system_data(client):
    resp = client.get('/api/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'cpu_percent' in data
    assert 'ram_percent' in data
    assert 'disk_percent' in data
    assert 'uptime' in data
    assert isinstance(data['cpu_percent'], (int, float))

def test_api_wallpaper_get(client):
    resp = client.get('/api/wallpaper')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'type' in data
    assert 'value' in data

def test_api_wallpaper_set(client):
    resp = client.post('/api/wallpaper',
                       data=json.dumps({'type': 'gradient', 'value': 'linear-gradient(red, blue)'}),
                       content_type='application/json')
    assert resp.status_code == 200
    resp2 = client.get('/api/wallpaper')
    data = resp2.get_json()
    assert data['type'] == 'gradient'

# ── App Pages ──

def test_all_app_pages_load(client):
    discover_apps()
    for app_id in get_apps().keys():
        resp = client.get(f'/app/{app_id}')
        assert resp.status_code == 200, f"App page /app/{app_id} returned {resp.status_code}"
        html = resp.data.decode()
        assert '← Dashboard' in html, f"/app/{app_id} missing back button"

def test_unknown_app_returns_404(client):
    resp = client.get('/app/nonexistent')
    assert resp.status_code == 404

# ── App-specific API routes ──

def test_snackscout_foods_api(client):
    resp = client.get('/app/snackscout/api/foods')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'name' in data[0]

def test_worldclock_time_api(client):
    resp = client.get('/app/worldclock/api/time')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 10
    cities = {z['city'] for z in data}
    assert 'Tokyo' in cities
    assert 'London' in cities

def test_monitor_history_api(client):
    resp = client.get('/app/monitor/api/history')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'cpu_history' in data
    assert 'ram_total' in data
    assert 'processes' in data

def test_notes_api_crud(client):
    # Create
    note = {'id': 'test_1', 'title': 'Test Note', 'body': 'Hello'}
    resp = client.post('/app/notes/api/notes',
                       data=json.dumps(note),
                       content_type='application/json')
    assert resp.status_code == 200
    # Read
    resp = client.get('/app/notes/api/notes')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(n['id'] == 'test_1' for n in data)
    # Delete
    resp = client.delete('/app/notes/api/notes/test_1')
    assert resp.status_code == 200
    resp = client.get('/app/notes/api/notes')
    data = resp.get_json()
    assert not any(n['id'] == 'test_1' for n in data)

def test_filemanager_ls_api(client):
    resp = client.get('/app/filemanager/api/ls')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'path' in data
    assert 'items' in data
    assert isinstance(data['items'], list)

# ── Static assets ──

def test_static_css_loads(client):
    resp = client.get('/static/css/dashboard.css')
    assert resp.status_code == 200

def test_static_js_loads(client):
    resp = client.get('/static/js/dashboard.js')
    assert resp.status_code == 200
