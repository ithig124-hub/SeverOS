import os, json
from flask import render_template, request, jsonify

def register(app, app_id):
    DATA_FILE = os.path.join('data', 'recipes.json')
    # Routes logic...
