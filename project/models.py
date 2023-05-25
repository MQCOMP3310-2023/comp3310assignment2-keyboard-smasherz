from . import db

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

class user(db.Model):
    email = db.Column(db.String(250), primary_key=True)
    password = db.Column(db.String(250), nullable=False)
    sessionToken = db.Column(db.String(250), nullable=False)
    rOwner = db.Column(db.boolean(), nullable=False)
    admin = db.Column(db.boolean(), nullable=False)

    @property
    def serialize(self):
    #Return object data in easily serializeable format"""
        return {
            'email'         : self.email,
            'password'      : self.password,
            'sessionT'      : self.sessionToken,
            'rOwner'        : self.rOwner,
            'admin'         : self.admin
        }
