from flask import Blueprint

def register(app, app_id):
    bp = Blueprint(app_id, __name__)
    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')
