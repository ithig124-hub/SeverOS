"""Tests for the Chad's Dashboard High-Fidelity UI Refactor."""

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


# ═══════ Wallpaper Background ═══════

class TestWallpaperBackground:
    def test_dashboard_has_wallpaper_bg_div(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'wallpaper-bg' in html
        assert 'wallpaperBg' in html

    def test_dashboard_has_wallpaper_overlay(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'wallpaper-overlay' in html

    def test_css_has_wallpaper_styles(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.wallpaper-bg' in css
        assert '.wallpaper-overlay' in css
        assert 'background-size: cover' in css

    def test_js_loads_wallpaper(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'loadWallpaper' in js
        assert '/api/wallpaper' in js


# ═══════ Top Greeting ═══════

class TestTopGreeting:
    def test_greeting_contains_strawhaithi(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'StrawHaIthi' in html

    def test_greeting_has_large_text_class(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'greeting-text' in html

    def test_css_greeting_is_large(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.greeting-text' in css
        assert '36px' in css or 'font-size' in css

    def test_js_updates_greeting_with_name(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'StrawHaIthi' in js


# ═══════ Widget Bar ═══════

class TestWidgetBar:
    def test_has_widget_bar(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'widget-bar' in html

    def test_has_quick_folders(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'quick-folders-grid' in html
        assert 'Downloads' in html
        assert 'Documents' in html
        assert 'Photos' in html
        assert 'Videos' in html

    def test_quick_folders_are_2x2_grid(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.quick-folders-grid' in css
        assert 'grid-template-columns: 1fr 1fr' in css

    def test_has_storage_widget(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'storage-widget-card' in html
        assert 'storageWidgetFill' in html
        assert 'storageUsedLabel' in html
        assert 'storageTotalLabel' in html
        assert 'TB' in html

    def test_storage_widget_has_progress_bar(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.storage-widget-bar' in css
        assert '.storage-widget-fill' in css

    def test_has_metric_chips(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'metric-chip' in html
        assert 'cpuChip' in html
        assert 'ramChip' in html
        assert 'diskChip' in html
        assert 'cpuValue' in html
        assert 'ramValue' in html
        assert 'diskValue' in html

    def test_metric_chips_have_labels(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'CPU' in html
        assert 'Memory' in html
        assert 'Storage' in html


# ═══════ Glassmorphism Styling ═══════

class TestGlassmorphism:
    def test_css_has_glassmorphism_variables(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '--glass-bg' in css
        assert '--glass-blur' in css
        assert 'rgba(20, 20, 30, 0.6)' in css

    def test_css_uses_backdrop_filter(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'backdrop-filter' in css
        assert 'blur(20px)' in css

    def test_css_card_radius_12px(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '--glass-radius: 12px' in css

    def test_css_icon_radius_10px(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'border-radius: 10px' in css

    def test_widget_cards_use_glass(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.widget-card' in css
        assert '.metric-chip' in css

    def test_dock_uses_glass(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.bottom-dock' in css


# ═══════ App Grid ═══════

class TestAppGrid:
    def test_squircle_icons(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'app-squircle' in html
        assert 'app-emoji' in html

    def test_grid_spacing_24px(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'gap: 24px' in css

    def test_all_16_apps_present(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        for name in ['3D Globe', 'SnackScout', 'Library', 'Map Explorer',
                     'Universal Search', 'Notes', 'Smart Dashboard',
                     'GPS Tracker', 'Wallpaper Manager', 'World Clock',
                     'System Monitor', 'File Manager',
                     'Multi-Source Dashboard', 'Alert System', 'Automation Engine', 'Network &amp; Comms']:
            assert name in html, f"Dashboard missing app: {name}"


# ═══════ Bottom Dock ═══════

class TestBottomDock:
    def test_has_bottom_dock(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'bottom-dock' in html
        assert 'bottomDock' in html

    def test_dock_has_multiple_icons(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        count = html.count('dock-icon')
        assert count >= 6, f"Expected at least 6 dock icons, found {count}"

    def test_dock_is_floating(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'position: fixed' in css
        assert 'bottom:' in css

    def test_dock_is_translucent(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        # The dock should use glass/backdrop-filter
        assert '.bottom-dock' in css


# ═══════ Search ═══════

class TestSearch:
    def test_has_search_float_button(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'search-float' in html
        assert 'searchFloatBtn' in html

    def test_has_search_modal(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'search-modal' in html
        assert 'searchInput' in html

    def test_search_is_translucent(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.search-float-btn' in css

    def test_js_has_search_functions(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'openSearch' in js
        assert 'closeSearch' in js
        assert 'searchInput' in js


# ═══════ Widget Stats API ═══════

class TestWidgetStatsAPI:
    def test_widget_stats_endpoint_exists(self, client):
        resp = client.get('/api/widget/stats')
        assert resp.status_code == 200

    def test_widget_stats_has_cpu(self, client):
        resp = client.get('/api/widget/stats')
        data = resp.get_json()
        assert 'cpu_percent' in data
        assert isinstance(data['cpu_percent'], (int, float))

    def test_widget_stats_has_ram(self, client):
        resp = client.get('/api/widget/stats')
        data = resp.get_json()
        assert 'ram_percent' in data

    def test_widget_stats_has_disk(self, client):
        resp = client.get('/api/widget/stats')
        data = resp.get_json()
        assert 'disk_percent' in data

    def test_widget_stats_has_storage_tb(self, client):
        resp = client.get('/api/widget/stats')
        data = resp.get_json()
        assert 'storage_used_tb' in data
        assert 'storage_total_tb' in data
        assert 'storage_percent' in data
        assert isinstance(data['storage_used_tb'], (int, float))
        assert isinstance(data['storage_total_tb'], (int, float))

    def test_widget_stats_storage_linked(self, client):
        """Verify widget stats uses storage_manager data."""
        resp = client.get('/api/widget/stats')
        data = resp.get_json()
        assert data['storage_total_tb'] > 0 or data['storage_total_tb'] == 0


# ═══════ Functional: Live Stats Wiring ═══════

class TestLiveStatsWiring:
    def test_js_calls_widget_stats_endpoint(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert '/api/widget/stats' in js
        assert 'fetchWidgetStats' in js

    def test_js_updates_metric_chips(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'cpuVal' in js or 'cpuValue' in js
        assert 'ramVal' in js or 'ramValue' in js
        assert 'diskVal' in js or 'diskValue' in js

    def test_js_updates_storage_widget(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'storageWidgetFill' in js
        assert 'storageUsedLabel' in js
        assert 'storageTotalLabel' in js

    def test_js_polls_stats_periodically(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'setInterval' in js
        assert 'fetchWidgetStats' in js


# ═══════ App Frame Compat ═══════

class TestAppFrameCompat:
    def test_all_apps_still_open(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            assert resp.status_code == 200, f"/app/{app_id} returned {resp.status_code}"

    def test_all_app_pages_have_back_button(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            html = resp.data.decode()
            assert '← Dashboard' in html, f"/app/{app_id} missing back button"

    def test_all_app_pages_use_dashboard_css(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            html = resp.data.decode()
            assert 'dashboard.css' in html

    def test_existing_api_endpoints_intact(self, client):
        for endpoint in ['/api/apps', '/api/stats', '/api/wallpaper',
                         '/api/storage/health', '/api/storage/drives']:
            resp = client.get(endpoint)
            assert resp.status_code == 200, f"{endpoint} returned {resp.status_code}"


# ═══════ Backward Compatibility ═══════

class TestBackwardCompat:
    def test_sidebar_element_exists(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'sidebar' in html
        assert 'sidebar-nav' in html

    def test_nav_items_exist(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'Home' in html
        assert 'App Store' in html
        assert 'Storage' in html
        assert 'System Monitor' in html
        assert 'File Manager' in html
        assert 'Settings' in html

    def test_legacy_section_ids(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'sectionHome' in html
        assert 'sectionAppStore' in html
        assert 'sectionStorage' in html
        assert 'appStoreGrid' in html
        assert 'diskHealthList' in html
        assert 'externalDrivesList' in html

    def test_greeting_id_exists(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'greetingText' in html

    def test_clock_id_exists(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'headerClock' in html

    def test_serveros_branding(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'ServerOS' in html
