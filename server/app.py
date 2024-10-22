#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

# Set up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-RESTful API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Route to get all restaurants
@app.route('/restaurants')
def restaurants():
    restaurants = Restaurant.query.all()
    return make_response(jsonify([restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants]), 200)

# Route to get or delete a specific restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_id(id):
    # Fetch the restaurant by ID using the session's get method
    restaurant = db.session.get(Restaurant, id)
    
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    if request.method == 'GET':
        return make_response(jsonify(restaurant.to_dict()), 200)
    
    if request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)

# Route to get all pizzas
@app.route('/pizzas')
def pizzas():
    pizzas = Pizza.query.all()
    return make_response(jsonify([pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]), 200)

# Route to create a new restaurant pizza relationship
@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    data = request.get_json()

    if not data:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not all([price, pizza_id, restaurant_id]):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    try:
        price = int(price)
        pizza_id = int(pizza_id)
        restaurant_id = int(restaurant_id)
    except ValueError:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    if price < 1 or price > 30:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    # Fetch restaurant and pizza by their IDs
    restaurant = db.session.get(Restaurant, restaurant_id)
    pizza = db.session.get(Pizza, pizza_id)

    if not restaurant or not pizza:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    # Create a new RestaurantPizza record
    restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    db.session.add(restaurant_pizza)
    db.session.commit()

    return make_response(jsonify(restaurant_pizza.to_dict()), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
