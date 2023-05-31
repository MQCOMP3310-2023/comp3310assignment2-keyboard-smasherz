from . import db
from flask import current_app
from flask_login import UserMixin
from flask_security import RoleMixin

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    @property
    def serialize(self):
    #Return object data in easily serializeable format"""
        return {
            'name'         : self.name,
            'id'           : self.id,
        }
    
class requestedRestaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)

    @property
    def serialize(self):
    #Return object data in easily serializeable format"""
        return {
            'name'         : self.name,
            'address'      : self.address,
            'id'           : self.id,
        }


class menu_item(db.Model):
    name = db.Column(db.String(80), nullable = False)
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer,db.ForeignKey('restaurant.id'))
    restaurant = db.    relationship(Restaurant)

    @property
    def serialize(self):
    #   """Return object data in easily serializeable format"""
        return {
            'name'       : self.name,
            'description' : self.description,
            'id'         : self.id,
            'price'      : self.price,
            'course'     : self.course,
        }

class role(RoleMixin, db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class user(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roles = db.relationship('role', secondary='user_roles')
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class user_roles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('Role.id', ondelete='CASCADE'))