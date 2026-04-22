from flask import Blueprint, jsonify

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/history')
    def history():
        try:
            import psutil, time
            cpu_times = []
            for _ in range(10):
                cpu_times.append(psutil.cpu_percent(interval=0.1))
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            net = psutil.net_io_counters()
            procs = []
            for p in sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']), key=lambda x: x.info.get('cpu_percent',0) or 0, reverse=True)[:15]:
                procs.append(p.info)
            temps = {}
            try:
                for name, entries in psutil.sensors_temperatures().items():
                    for e in entries:
                        temps[e.label or name] = round(e.current, 1)
            except Exception:
                pass
            return jsonify({
                'cpu_history': cpu_times,
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': getattr(psutil.cpu_freq(), 'current', 0) if psutil.cpu_freq() else 0,
                'ram_total': mem.total,
                'ram_used': mem.used,
                'ram_available': mem.available,
                'ram_percent': mem.percent,
                'swap_total': psutil.swap_memory().total,
                'swap_used': psutil.swap_memory().used,
                'swap_percent': psutil.swap_memory().percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_percent': disk.percent,
                'disk_read': disk_io.read_bytes if disk_io else 0,
                'disk_write': disk_io.write_bytes if disk_io else 0,
                'net_sent': net.bytes_sent,
                'net_recv': net.bytes_recv,
                'temperatures': temps,
                'processes': procs,
                'boot_time': psutil.boot_time(),
            })
        except ImportError:
            return jsonify({'error': 'psutil not installed'}), 500

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
