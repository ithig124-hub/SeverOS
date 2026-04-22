from flask import Blueprint, jsonify

def register(app, app_id):
    bp = Blueprint(app_id, __name__)

    @bp.route('/api/foods')
    def foods():
        return jsonify(_FOODS)

    app.register_blueprint(bp, url_prefix=f'/app/{app_id}')

_FOODS = [
    {"id":1,"name":"Instant Ramen","cat":"Meals","price":1.20,"store":"Aldi","img":"🍜","tags":["cheap","quick"],"cal":380},
    {"id":2,"name":"Greek Yoghurt","cat":"Dairy","price":4.50,"store":"Woolworths","img":"🥛","tags":["healthy","protein"],"cal":100},
    {"id":3,"name":"Banana Bunch","cat":"Fruits","price":2.80,"store":"Coles","img":"🍌","tags":["cheap","healthy"],"cal":105},
    {"id":4,"name":"Doritos","cat":"Snacks","price":3.50,"store":"Woolworths","img":"🌮","tags":["party"],"cal":260},
    {"id":5,"name":"Chicken Breast 500g","cat":"Meat","price":7.00,"store":"Coles","img":"🍗","tags":["protein","gym"],"cal":165},
    {"id":6,"name":"Tim Tams","cat":"Snacks","price":3.65,"store":"Woolworths","img":"🍫","tags":["study"],"cal":95},
    {"id":7,"name":"Iced Coffee 500ml","cat":"Beverages","price":4.20,"store":"7-Eleven","img":"☕","tags":["study","quick"],"cal":200},
    {"id":8,"name":"Sourdough Loaf","cat":"Bakery","price":5.00,"store":"IGA","img":"🍞","tags":["healthy"],"cal":120},
    {"id":9,"name":"Avocado 2pk","cat":"Fruits","price":4.00,"store":"Aldi","img":"🥑","tags":["healthy"],"cal":160},
    {"id":10,"name":"Mi Goreng 5pk","cat":"Meals","price":3.00,"store":"Coles","img":"🍝","tags":["cheap","quick","study"],"cal":400},
    {"id":11,"name":"Shapes BBQ","cat":"Snacks","price":2.50,"store":"Woolworths","img":"🔶","tags":["party","cheap"],"cal":220},
    {"id":12,"name":"Protein Bar","cat":"Snacks","price":3.00,"store":"Chemist","img":"💪","tags":["gym","protein"],"cal":200},
]
