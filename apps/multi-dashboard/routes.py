"""Multi-Source Dashboard – API routes with lightweight caching for Pi Zero."""

import time
import json
from flask import Blueprint, jsonify

# ── Pi Zero Optimization: Simple in-memory cache ──
_cache = {}
_CACHE_TTL = 30  # seconds

def _cached(key, ttl=_CACHE_TTL):
    """Return cached value if still fresh, else None."""
    entry = _cache.get(key)
    if entry and (time.time() - entry['ts']) < ttl:
        return entry['data']
    return None

def _set_cache(key, data):
    _cache[key] = {'data': data, 'ts': time.time()}


def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/dashboard/weather')
    def dashboard_weather():
        cached = _cached('weather')
        if cached:
            return jsonify(cached)
        data = {
            'location': 'San Francisco, CA',
            'temperature_c': 18.5,
            'temperature_f': 65.3,
            'condition': 'Partly Cloudy',
            'icon': '⛅',
            'humidity': 62,
            'wind_speed_kmh': 14.2,
            'wind_direction': 'WSW',
            'uv_index': 4,
            'feels_like_c': 17.0,
            'forecast': [
                {'day': 'Mon', 'high_c': 20, 'low_c': 13, 'icon': '☀️', 'condition': 'Sunny'},
                {'day': 'Tue', 'high_c': 19, 'low_c': 12, 'icon': '⛅', 'condition': 'Partly Cloudy'},
                {'day': 'Wed', 'high_c': 17, 'low_c': 11, 'icon': '🌧', 'condition': 'Rain'},
                {'day': 'Thu', 'high_c': 21, 'low_c': 14, 'icon': '☀️', 'condition': 'Sunny'},
                {'day': 'Fri', 'high_c': 22, 'low_c': 15, 'icon': '🌤', 'condition': 'Mostly Sunny'},
            ],
            'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }
        _set_cache('weather', data)
        return jsonify(data)

    @bp.route('/api/dashboard/stocks')
    def dashboard_stocks():
        cached = _cached('stocks')
        if cached:
            return jsonify(cached)
        data = {
            'market_status': 'open',
            'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'tickers': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 189.84, 'change': 2.31, 'change_pct': 1.23, 'volume': '52.3M'},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 141.70, 'change': -0.56, 'change_pct': -0.39, 'volume': '18.7M'},
                {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 378.91, 'change': 4.12, 'change_pct': 1.10, 'volume': '21.1M'},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 248.42, 'change': -3.18, 'change_pct': -1.26, 'volume': '98.4M'},
                {'symbol': 'AMZN', 'name': 'Amazon.com', 'price': 178.25, 'change': 1.87, 'change_pct': 1.06, 'volume': '44.6M'},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'price': 875.28, 'change': 12.45, 'change_pct': 1.44, 'volume': '35.2M'},
            ],
            'indices': [
                {'name': 'S&P 500', 'value': 5021.84, 'change': 15.29, 'change_pct': 0.31},
                {'name': 'NASDAQ', 'value': 15990.66, 'change': 67.08, 'change_pct': 0.42},
                {'name': 'DOW', 'value': 38996.39, 'change': -12.37, 'change_pct': -0.03},
            ]
        }
        _set_cache('stocks', data)
        return jsonify(data)

    @bp.route('/api/dashboard/network')
    def dashboard_network():
        cached = _cached('network')
        if cached:
            return jsonify(cached)
        try:
            import psutil
            net = psutil.net_io_counters()
            addrs = {}
            for iface, addr_list in psutil.net_if_addrs().items():
                for addr in addr_list:
                    if addr.family == 2:  # AF_INET
                        addrs[iface] = addr.address
            net_stats = {}
            for iface, stats in psutil.net_if_stats().items():
                net_stats[iface] = {'is_up': stats.isup, 'speed_mbps': stats.speed}
            data = {
                'bytes_sent': net.bytes_sent,
                'bytes_recv': net.bytes_recv,
                'packets_sent': net.packets_sent,
                'packets_recv': net.packets_recv,
                'interfaces': addrs,
                'interface_stats': net_stats,
                'active_connections': len(psutil.net_connections(kind='inet')),
                'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
        except ImportError:
            data = {
                'bytes_sent': 1048576000,
                'bytes_recv': 5242880000,
                'packets_sent': 842000,
                'packets_recv': 1250000,
                'interfaces': {'eth0': '192.168.1.100', 'wlan0': '192.168.1.101'},
                'interface_stats': {
                    'eth0': {'is_up': True, 'speed_mbps': 1000},
                    'wlan0': {'is_up': True, 'speed_mbps': 150},
                },
                'active_connections': 42,
                'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
        _set_cache('network', data)
        return jsonify(data)

    @bp.route('/api/dashboard/system')
    def dashboard_system():
        cached = _cached('system', ttl=5)
        if cached:
            return jsonify(cached)
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.3)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            boot = psutil.boot_time()
            uptime_sec = int(time.time() - boot)
            hours, remainder = divmod(uptime_sec, 3600)
            minutes, _ = divmod(remainder, 60)
            data = {
                'cpu_percent': cpu,
                'cpu_count': psutil.cpu_count(),
                'ram_percent': mem.percent,
                'ram_used_gb': round(mem.used / (1024**3), 2),
                'ram_total_gb': round(mem.total / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'uptime': f"{hours}h {minutes}m",
                'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
        except ImportError:
            data = {
                'cpu_percent': 23.5,
                'cpu_count': 4,
                'ram_percent': 58.2,
                'ram_used_gb': 0.30,
                'ram_total_gb': 0.51,
                'disk_percent': 44.0,
                'disk_used_gb': 6.8,
                'disk_total_gb': 15.5,
                'uptime': '48h 12m',
                'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
        _set_cache('system', data)
        return jsonify(data)

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
