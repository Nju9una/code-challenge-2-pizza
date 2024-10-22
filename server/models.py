from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Configure naming conventions for database constraints to ensure consistency and avoid conflicts
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String) 
    address = db.Column(db.String) 

    # One-to-many relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    # Association proxy to easily access related pizzas
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Serialization rules to exclude nested relationships
    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # One-to-many relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')
    # Association proxy to easily access related restaurants
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Serialization rules to exclude nested relationships
    serialize_rules = ('-restaurant_pizzas', '-restaurants')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))

    # Many-to-one relationship with Restaurant
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    # Many-to-one relationship with Pizza
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # Serialization rules to exclude nested relationships
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # Validator for the price field to ensure it is between 1 and 30
    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30.")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
