"""Tests for the Umbrel UI refactor – new layout, storage, and app framing."""

import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, discover_apps, get_apps


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ═══════ Dashboard Layout Tests ═══════

class TestUmbrelDashboard:
    def test_dashboard_has_sidebar(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'sidebar' in html
        assert 'sidebar-nav' in html

    def test_dashboard_has_sidebar_nav_items(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'Home' in html
        assert 'App Store' in html
        assert 'Storage' in html
        assert 'System Monitor' in html
        assert 'File Manager' in html
        assert 'Settings' in html

    def test_dashboard_has_header_with_search(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'searchInput' in html
        assert 'Search apps' in html

    def test_dashboard_has_system_stat_chips(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'cpuChip' in html
        assert 'ramChip' in html
        assert 'tempChip' in html

    def test_dashboard_has_app_grid(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'app-grid' in html
        assert 'appGrid' in html

    def test_dashboard_uses_squircle_icons(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'app-squircle' in html
        assert 'app-emoji' in html

    def test_dashboard_lists_all_16_apps(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        for name in ['3D Globe', 'SnackScout', 'Library', 'Map Explorer',
                     'Universal Search', 'Notes', 'Smart Dashboard',
                     'GPS Tracker', 'Wallpaper Manager', 'World Clock',
                     'System Monitor', 'File Manager',
                     'Multi-Source Dashboard', 'Alert System', 'Automation Engine', 'Network &amp; Comms']:
            assert name in html, f"Dashboard missing app: {name}"

    def test_dashboard_has_storage_section(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'sectionStorage' in html
        assert 'diskHealthList' in html
        assert 'externalDrivesList' in html

    def test_dashboard_has_appstore_section(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'sectionAppStore' in html
        assert 'appStoreGrid' in html

    def test_dashboard_has_clock(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'headerClock' in html

    def test_dashboard_has_greeting(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'greetingText' in html

    def test_serverOS_branding(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'ServerOS' in html


# ═══════ CSS Tests ═══════

class TestUmbrelCSS:
    def test_css_loads(self, client):
        resp = client.get('/static/css/dashboard.css')
        assert resp.status_code == 200

    def test_css_has_dark_theme(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '#000000' in css or '--bg-base: #000000' in css

    def test_css_has_sidebar_styles(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.sidebar' in css
        assert '.sidebar-nav' in css

    def test_css_has_squircle_styles(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.app-squircle' in css
        assert 'squircle' in css

    def test_css_has_inter_font(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert "'Inter'" in css

    def test_css_has_fast_transitions(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'transition-fast' in css

    def test_css_has_app_page_styles(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.app-page' in css
        assert '.app-topbar' in css
        assert '.back-btn' in css
        assert '.glass-panel' in css


# ═══════ JS Tests ═══════

class TestUmbrelJS:
    def test_js_loads(self, client):
        resp = client.get('/static/js/dashboard.js')
        assert resp.status_code == 200

    def test_js_has_search_functionality(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'searchInput' in js
        assert 'hidden' in js

    def test_js_has_sidebar_navigation(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'switchSection' in js
        assert 'navItems' in js

    def test_js_has_stats_polling(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'fetchStats' in js
        assert '/api/stats' in js

    def test_js_has_storage_loading(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'loadStorage' in js
        assert 'loadDiskHealth' in js
        assert 'loadExternalDrives' in js

    def test_js_has_mobile_sidebar(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'openMobileSidebar' in js
        assert 'closeMobileSidebar' in js


# ═══════ Storage API Tests ═══════

class TestStorageAPI:
    def test_storage_health_endpoint(self, client):
        resp = client.get('/api/storage/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        if data:
            disk = data[0]
            assert 'device' in disk
            assert 'mount' in disk
            assert 'total_bytes' in disk
            assert 'used_bytes' in disk
            assert 'percent_used' in disk
            assert 'total_human' in disk

    def test_storage_drives_endpoint(self, client):
        resp = client.get('/api/storage/drives')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_storage_mount_requires_device(self, client):
        resp = client.post('/api/storage/mount',
                          data=json.dumps({}),
                          content_type='application/json')
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['success'] is False

    def test_storage_unmount_requires_mountpoint(self, client):
        resp = client.post('/api/storage/unmount',
                          data=json.dumps({}),
                          content_type='application/json')
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['success'] is False


# ═══════ Storage Manager Unit Tests ═══════

class TestStorageManager:
    def test_import(self):
        from core.storage_manager import (
            list_block_devices, get_external_drives,
            get_disk_health, mount_drive, unmount_drive,
            _human_size
        )

    def test_human_size(self):
        from core.storage_manager import _human_size
        assert _human_size(0) == '0 B'
        assert _human_size(1024) == '1.0 KB'
        assert _human_size(1048576) == '1.0 MB'
        assert _human_size(1073741824) == '1.0 GB'
        assert _human_size(1099511627776) == '1.0 TB'
        assert '500' in _human_size(500)

    def test_get_disk_health_returns_list(self):
        from core.storage_manager import get_disk_health
        result = get_disk_health()
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'device' in result[0]
        assert 'percent_used' in result[0]

    def test_get_external_drives_returns_list(self):
        from core.storage_manager import get_external_drives
        result = get_external_drives()
        assert isinstance(result, list)

    @patch('core.storage_manager._run')
    def test_list_block_devices_parses_json(self, mock_run):
        from core.storage_manager import list_block_devices
        mock_run.return_value = json.dumps({
            "blockdevices": [
                {"name": "sda", "size": "1000000000", "type": "disk", "rm": True, "tran": "usb"}
            ]
        })
        result = list_block_devices()
        assert len(result) == 1
        assert result[0]['name'] == 'sda'

    @patch('core.storage_manager._run')
    def test_list_block_devices_handles_empty(self, mock_run):
        from core.storage_manager import list_block_devices
        mock_run.return_value = ''
        result = list_block_devices()
        assert result == []

    @patch('core.storage_manager._run')
    def test_get_external_drives_filters_usb(self, mock_run):
        from core.storage_manager import get_external_drives
        mock_run.return_value = json.dumps({
            "blockdevices": [
                {"name": "sda", "size": 500000000, "type": "disk", "rm": True, "tran": "usb",
                 "model": "USB Drive", "serial": "12345", "hotplug": True,
                 "children": [
                     {"name": "sda1", "size": 499000000, "type": "part", "fstype": "ext4",
                      "mountpoint": "/mnt/usb", "label": "data"}
                 ]},
                {"name": "nvme0n1", "size": 1000000000, "type": "disk", "rm": False, "tran": "nvme",
                 "model": "NVMe SSD", "serial": "abc", "hotplug": False},
            ]
        })
        result = get_external_drives()
        assert len(result) == 1
        assert result[0]['name'] == 'sda'
        assert result[0]['model'] == 'USB Drive'
        assert len(result[0]['partitions']) == 1

    def test_fallback_disk_health(self):
        from core.storage_manager import _fallback_disk_health
        result = _fallback_disk_health()
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0]['mount'] == '/'


# ═══════ All app pages open within Umbrel frame ═══════

class TestAppPagesInFrame:
    def test_all_app_pages_have_back_button(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            assert resp.status_code == 200, f"/app/{app_id} returned {resp.status_code}"
            html = resp.data.decode()
            assert '← Dashboard' in html, f"/app/{app_id} missing back button"

    def test_all_app_pages_use_base_template_styles(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            html = resp.data.decode()
            assert 'dashboard.css' in html, f"/app/{app_id} not loading dashboard.css"
            assert 'app-topbar' in html, f"/app/{app_id} missing app-topbar"

    def test_ported_modules_accessible(self, client):
        ported = ['globe', 'snackscout', 'library', 'map', 'search',
                  'notes', 'tracking', 'worldclock']
        for app_id in ported:
            resp = client.get(f'/app/{app_id}')
            assert resp.status_code == 200, f"Ported module /app/{app_id} not accessible"


# ═══════ Auto-registration ═══════

class TestAutoRegistration:
    def test_all_16_apps_discovered(self):
        discover_apps()
        apps = get_apps()
        expected = {'globe', 'snackscout', 'library', 'map', 'search', 'notes',
                    'dashboard', 'tracking', 'wallpaper', 'worldclock', 'monitor', 'filemanager',
                    'multi-dashboard', 'alerts', 'automation', 'network'}
        assert set(apps.keys()) == expected

    def test_manifest_fields_preserved(self):
        discover_apps()
        for app_id, manifest in get_apps().items():
            assert 'name' in manifest
            assert 'icon' in manifest
            assert 'description' in manifest
            assert 'color' in manifest
            assert 'category' in manifest


# ═══════ Existing API compatibility ═══════

class TestExistingAPICompat:
    def test_api_apps(self, client):
        resp = client.get('/api/apps')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 16

    def test_api_stats(self, client):
        resp = client.get('/api/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'cpu_percent' in data
        assert 'ram_percent' in data

    def test_api_wallpaper(self, client):
        resp = client.get('/api/wallpaper')
        assert resp.status_code == 200
