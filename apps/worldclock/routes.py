from flask import Blueprint, jsonify
import datetime

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/time')
    def world_time():
        import time as _time
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        zones = [
            {"city":"New York","tz":"America/New_York","offset":-4},
            {"city":"London","tz":"Europe/London","offset":0},
            {"city":"Paris","tz":"Europe/Paris","offset":1},
            {"city":"Dubai","tz":"Asia/Dubai","offset":4},
            {"city":"Mumbai","tz":"Asia/Kolkata","offset":5.5},
            {"city":"Singapore","tz":"Asia/Singapore","offset":8},
            {"city":"Tokyo","tz":"Asia/Tokyo","offset":9},
            {"city":"Sydney","tz":"Australia/Sydney","offset":10},
            {"city":"Perth","tz":"Australia/Perth","offset":8},
            {"city":"Los Angeles","tz":"America/Los_Angeles","offset":-7},
            {"city":"São Paulo","tz":"America/Sao_Paulo","offset":-3},
            {"city":"Johannesburg","tz":"Africa/Johannesburg","offset":2},
        ]
        for z in zones:
            local = utc_now + datetime.timedelta(hours=z['offset'])
            z['time'] = local.strftime('%H:%M:%S')
            z['date'] = local.strftime('%a %d %b')
            z['hour'] = local.hour
        return jsonify(zones)

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
