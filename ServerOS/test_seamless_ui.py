"""Tests for the ServerOS Seamless Smooth UI Refactor."""

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


# ═══════ 1. Smooth Vertical Scroll ═══════

class TestSmoothScroll:
    def test_html_has_scroll_behavior_smooth(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'scroll-behavior: smooth' in css

    def test_dashboard_shell_scrollable(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.dashboard-shell' in css
        assert 'overflow-y: auto' in css

    def test_content_section_no_own_scroll(self, client):
        """Content sections should not have their own overflow-y: auto anymore."""
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        # Check .content-section block doesn't have overflow-y: auto
        import re
        cs_block = re.search(r'\.content-section\s*\{[^}]+\}', css)
        assert cs_block is not None
        block_text = cs_block.group()
        assert 'overflow-y: auto' not in block_text


# ═══════ 2. Staggered Entrance Animations ═══════

class TestStaggeredAnimations:
    def test_css_has_tile_stagger_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'tileStaggerIn' in css

    def test_css_has_widget_stagger_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'widgetStaggerIn' in css

    def test_css_has_chip_stagger_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'chipStaggerIn' in css

    def test_tile_animation_delays_exist(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        for i in range(1, 13):
            assert f'.app-tile:nth-child({i})' in css

    def test_widget_card_animation_delays(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.widget-card:nth-child(1)' in css
        assert '.widget-card:nth-child(2)' in css
        assert '.widget-card:nth-child(3)' in css

    def test_metric_chip_animation_delays(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.metric-chip:nth-child(1)' in css
        assert '.metric-chip:nth-child(2)' in css
        assert '.metric-chip:nth-child(3)' in css


# ═══════ 3. Parallax / Fixed Wallpaper ═══════

class TestParallaxWallpaper:
    def test_wallpaper_has_fixed_attachment(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'background-attachment: fixed' in css

    def test_wallpaper_bg_still_exists(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'wallpaper-bg' in html
        assert 'wallpaperBg' in html


# ═══════ 4. Hover & Interaction Effects ═══════

class TestHoverInteraction:
    def test_app_tile_hover_scale(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'scale(1.05)' in css

    def test_widget_card_hover_scale(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        # Widget card hover has scale
        assert '.widget-card:hover' in css
        assert 'scale(1.02)' in css

    def test_metric_chip_hover_scale(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.metric-chip:hover' in css

    def test_glow_effect_on_hover(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '--glass-glow' in css

    def test_active_state_app_tile(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.app-tile:active' in css

    def test_active_state_widget_card(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.widget-card:active' in css

    def test_active_state_metric_chip(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.metric-chip:active' in css

    def test_dock_icon_hover_lift(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.dock-icon:hover' in css
        assert 'translateY(-4px)' in css

    def test_dock_icon_active_state(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.dock-icon:active' in css


# ═══════ 5. Floating Dock & Header Animation ═══════

class TestDockAndHeader:
    def test_dock_frosted_blur(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'blur(28px)' in css
        assert 'saturate' in css

    def test_dock_entrance_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'dockSlideIn' in css

    def test_header_entrance_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'headerSlideIn' in css

    def test_greeting_has_entrance_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.top-greeting' in css
        assert 'headerSlideIn' in css

    def test_dock_is_fixed(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.bottom-dock' in css
        assert 'position: fixed' in css


# ═══════ 6. Seamless App Transitions ═══════

class TestAppTransitions:
    def test_html_has_app_frame_overlay(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'app-frame-overlay' in html
        assert 'appFrameOverlay' in html
        assert 'appFrameIframe' in html
        assert 'appFrameBackBtn' in html

    def test_css_has_app_frame_styles(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.app-frame-overlay' in css
        assert '.app-frame-overlay.visible' in css
        assert '.app-frame-overlay.closing' in css

    def test_css_frame_zoom_transition(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'scale(0.92)' in css

    def test_js_has_open_app_in_frame(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'openAppInFrame' in js

    def test_js_has_close_app_frame(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'closeAppFrame' in js

    def test_back_to_home_button_in_frame(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'Back to Home' in html

    def test_app_frame_has_iframe(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'app-frame-iframe' in html

    def test_js_intercepts_tile_clicks(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'closest' in js
        assert 'app-tile' in js
        assert 'openAppInFrame' in js

    def test_js_listens_for_postmessage(self, client):
        resp = client.get('/static/js/dashboard.js')
        js = resp.data.decode()
        assert 'serveros-close-app' in js

    def test_app_base_sends_postmessage(self, client):
        """app_base.html should have script that posts close-app message."""
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            html = resp.data.decode()
            assert 'serveros-close-app' in html, f"/app/{app_id} missing postMessage close integration"
            break

    def test_app_page_zoom_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'appPageZoomIn' in css


# ═══════ 7. Glass Consistency ═══════

class TestGlassConsistency:
    def test_glass_shadow_variable(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '--glass-shadow' in css

    def test_glass_glow_variable(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '--glass-glow' in css

    def test_widget_card_uses_glass_shadow(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'var(--glass-shadow)' in css

    def test_store_card_uses_glass(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.store-card' in css

    def test_storage_panel_uses_glass(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.storage-panel' in css

    def test_glass_panel_app_pages_refined(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.glass-panel' in css

    def test_app_topbar_frosted(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '.app-topbar' in css


# ═══════ 8. Responsive Layout ═══════

class TestResponsiveLayout:
    def test_app_grid_autofill(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'auto-fill' in css
        assert 'minmax(100px' in css

    def test_responsive_breakpoints_exist(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert '@media (max-width: 900px)' in css
        assert '@media (max-width: 768px)' in css
        assert '@media (max-width: 480px)' in css


# ═══════ 9. Section Transitions ═══════

class TestSectionTransitions:
    def test_section_fade_in_animation(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'sectionFadeIn' in css

    def test_app_page_zoom_in(self, client):
        resp = client.get('/static/css/dashboard.css')
        css = resp.data.decode()
        assert 'appPageZoomIn' in css


# ═══════ 10. Backward Compatibility ═══════

class TestBackwardCompatSeamless:
    def test_all_apps_still_load(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            assert resp.status_code == 200

    def test_all_apps_have_back_button(self, client):
        discover_apps()
        for app_id in get_apps().keys():
            resp = client.get(f'/app/{app_id}')
            html = resp.data.decode()
            assert '← Dashboard' in html

    def test_existing_api_endpoints(self, client):
        for endpoint in ['/api/apps', '/api/stats', '/api/wallpaper',
                         '/api/storage/health', '/api/storage/drives']:
            resp = client.get(endpoint)
            assert resp.status_code == 200

    def test_sidebar_still_exists(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'sidebar' in html
        assert 'sidebar-nav' in html

    def test_legacy_ids_preserved(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        for elem_id in ['sectionHome', 'sectionAppStore', 'sectionStorage',
                        'appStoreGrid', 'diskHealthList', 'externalDrivesList',
                        'greetingText', 'headerClock', 'wallpaperBg',
                        'cpuChip', 'ramChip', 'diskChip', 'bottomDock']:
            assert elem_id in html, f"Missing element id: {elem_id}"

    def test_all_16_apps_in_grid(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        for name in ['3D Globe', 'SnackScout', 'Library', 'Map Explorer',
                     'Universal Search', 'Notes', 'Smart Dashboard',
                     'GPS Tracker', 'Wallpaper Manager', 'World Clock',
                     'System Monitor', 'File Manager',
                     'Multi-Source Dashboard', 'Alert System', 'Automation Engine', 'Network &amp; Comms']:
            assert name in html, f"Dashboard missing app: {name}"
