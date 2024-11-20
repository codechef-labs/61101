# models.py
# Models represent tables in database created with SQLAlchemy.

# Import necessary modules from SQLAlchemy and SerializerMixin for serialization.
import re

from config import bcrypt, db
from helpers import (
    dollar_to_cents,
    validate_not_blank,
    validate_positive_number,
    validate_type,
)
from sqlalchemy import MetaData, null
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Models go here!
# one to many relationship between order and order details
# one to many relationship between user and orders

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)


# Product Model
# This class represents the products (watches) that we're selling.
# Each product has an ID, name, description, price, quantity, and an image URL. Wonder how they get two images.
class Product(db.Model, SerializerMixin):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    item_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    imageAlt = db.Column(db.String(255))

    product_categories = db.relationship(
        "ProductCategory", back_populates="product", cascade="all, delete-orphan"
    )
    categories = association_proxy("product_categories", "category")

    serialize_rules = ("-product_categories",)

    # validations for Product Model
    @validates("name", "description", "image_url", "imageAlt")
    def validate_not_blank(self, key, value):
        return validate_not_blank(value, key)

    @validates("price")
    def validate_price(self, key, price):
        price_in_cents = validate_positive_number(dollar_to_cents(price), key)
        return price_in_cents

    @validates("item_quantity")
    def validate_item_quantity(self, key, item_quantity):
        item_quantity = validate_positive_number(item_quantity, key)
        return validate_type(item_quantity, key, int)

    def to_dict(self, convert_price_to_dollars=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price / 100 if convert_price_to_dollars else self.price,
            "item_quantity": self.item_quantity,
            "image_url": self.image_url,
            "imageAlt": self.imageAlt,
        }
        return data

    def __repr__(self):
        return f"<Product {self.name}>"


# Category Model
# This class represents the categories of products that we're selling.
# This is a many to many relationship between products and categories.
# Two categories Genesis and Elite but some products are in both categories as it is the first of the lineup.
class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    product_categories = db.relationship(
        "ProductCategory", back_populates="category", cascade="all, delete-orphan"
    )

    products = association_proxy("product_categories", "product")

    serialize_rules = ("-product_categories",)

    @validates("name")
    def validate_name(self, key, name):
        return validate_not_blank(name, key)

    def __repr__(self):
        return f"<Category {self.name}>"


# ProductCategory Model
# This class represents the relationship between products and categories.
# This is a many to many relationship between products and categories.
class ProductCategory(db.Model, SerializerMixin):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    product = db.relationship("Product", back_populates="product_categories")
    category = db.relationship("Category", back_populates="product_categories")

    serialize_rules = ("-product", "-category")

    @validates("product_id", "category_id")
    def validate_ids(self, key, value):
        value = validate_type(value, key, int)
        if value is None:
            raise ValueError(f"{key} must not be null.")
        return value

    def __repr__(self):
        return f"<ProductCategory Product: {self.product_id}, Category: {self.category_id}>"


# User Model
# This class represents the users of our site. They can buy products.
# Each user has an ID, username, email, and shipping address.
class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=False)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)
    shipping_address = db.Column((db.Text), nullable=False)
    shipping_city = db.Column(db.String(255), nullable=False)
    shipping_state = db.Column(db.String(255), nullable=False)
    shipping_zip = db.Column(db.String(255), nullable=False)

    orders = db.relationship("Order", back_populates="user")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("email")
    def validate_email(self, key, email):
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address.")
        return email

    @validates("username")
    def validate_username(self, key, username):
        return validate_not_blank(username, key)

    serialize_rules = ("-orders",)


# Order Model
# Represents an order made by a user. An order can contain multiple products.
class Order(db.Model, SerializerMixin):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    order_details = db.relationship("OrderDetail", back_populates="order")
    user = db.relationship("User", back_populates="orders")


# OrderDetail Model
# Links orders to products and includes the quantity of each product in an order.
class OrderDetail(db.Model, SerializerMixin):
    __tablename__ = "order_details"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship("Order", back_populates="order_details")
    product = db.relationship("Product")

    serialize_rules = (
        "-order",
        "-product",
    )
