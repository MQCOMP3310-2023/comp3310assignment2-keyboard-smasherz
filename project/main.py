from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Restaurant, menu_item, requested_restaurant, user
from flask_login import login_required, current_user
from flask_security import roles_accepted, Security
from sqlalchemy import asc
from . import db
import logging

main = Blueprint('main', __name__)
main_show_restaurants = 'main.show_restaurants'
main_show_menu = 'main.show_restaurants'

#Show all restaurants
@main.route('/')
@main.route('/restaurant/')
def show_restaurants():
    restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('restaurants.html', restaurants = restaurants)

#login
@main.route('/restaurant/login')
def login():
    return render_template('login.html')

def authenticate_session(admin=False):
    # if browsercookie == validsessioncookie
    return True

#Search for restaurants
@main.route('/restaurant/search/', methods=['GET'])
def search_restaurants():
    search_term = request.args.get('query')
    search_pattern = f"%{search_term}%"
    restaurants = db.session.query(Restaurant).filter(Restaurant.name.like(search_pattern)).order_by(asc(Restaurant.name)).all()

    if not restaurants:
        flash("No restaurants found. Please try again")

    return render_template('restaurants.html', restaurants=restaurants)

#Create a new restaurant
@main.route('/restaurant/new/', methods=['GET','POST'])
@login_required
@roles_accepted("admin")
def new_restaurant():
    access = authenticate_session()
    if access: #Admin or Restaurant Owner only
        if request.method == 'POST':
            new_restaurant = Restaurant(name = request.form['name'])
            db.session.add(new_restaurant)
            logging.info(f'{new_restaurant.name} added')
            flash('New Restaurant %s Successfully Created' % new_restaurant.name)
            db.session.commit()
            return redirect(url_for(main_show_restaurants))
        else:
            return render_template('newRestaurant.html')

#Request new restaurant 
@main.route('/restaurant/request/', methods=['GET','POST'])
@login_required
def request_restaurant():
    if request.method == 'POST':
        request_restaurant = requested_restaurant(name = request.form['name'], address = request.form['address'])
        db.session.add(request_restaurant)
        logging.info(f'{request_restaurant.name} request added')
        flash('New Restaurant %s Successfully Requested' % request_restaurant.name)
        db.session.commit()
        return redirect(url_for(main_show_restaurants))
    else:
        return render_template('requestRestaurant.html')

#Edit a restaurant
@main.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
@login_required
@roles_accepted("rOwner","admin")
def edit_restaurant(restaurant_id):
    access = authenticate_session()
    if access: #Admin or Restaurant Owner onl
        edited_restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
        if (current_user.restaurant == edited_restaurant.name) or (current_user.restaurant == "admin"):
            if request.method == 'POST':
                if request.form['name']:
                    edited_restaurant.name = request.form['name']
                    flash('Restaurant Successfully Edited %s' % edited_restaurant.name)
                    return redirect(url_for(main_show_restaurants))
            else:
                return render_template('editRestaurant.html', restaurant = edited_restaurant)
        else: 
            flash('You cant edit that, You do not own this restaurant!')
            return redirect(url_for('main.show_restaurants'))


#Delete a restaurant
@main.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
@login_required
@roles_accepted("admin")
def delete_restaurant(restaurant_id):
    access = authenticate_session() 
    edited_restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    if access: #Admin or Restaurant Owner only
        if (current_user.restaurant == edited_restaurant.name) or (current_user.restaurant == "admin"):
            restaurant_to_delete = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
            if request.method == 'POST':
                db.session.delete(restaurant_to_delete)
                logging.info(f'{restaurant_to_delete.name} deleted') 
                flash('%s Successfully Deleted' % restaurant_to_delete.name)
                db.session.commit()
                return redirect(url_for(main_show_restaurants, restaurant_id = restaurant_id))
            else:
                return render_template('deleteRestaurant.html',restaurant = restaurant_to_delete)
        else: 
            flash('You cant delete that, You do not own this restaurant!')
            return redirect(url_for('main.show_restaurants'))

#Show a restaurant menu
@main.route('/restaurant/<int:restaurant_id>/')
@main.route('/restaurant/<int:restaurant_id>/menu/')
def show_menu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = db.session.query(menu_item).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', items = items, restaurant = restaurant)


#Create a new menu item
@main.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
@login_required
@roles_accepted("rOwner","admin")
def new_menu_item(restaurant_id):
    access = authenticate_session()
    edited_restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    if access: #Admin or Restaurant Owner only
        if (current_user.restaurant == edited_restaurant.name) or (current_user.restaurant == "admin"):
            if request.method == 'POST':
                new_item = menu_item(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
                db.session.add(new_item)
                db.session.commit()
                logging.info(f'{new_item.name} item added') 
                flash('New Menu %s Item Successfully Created' % (new_item.name))
                return redirect(url_for(main_show_menu, restaurant_id = restaurant_id))
            else:
                return render_template('newmenuitem.html', restaurant_id = restaurant_id)
        else: 
            flash('You cant add that, You do not own this restaurant!')
            return redirect(url_for('main.show_restaurants'))

#Edit a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
@login_required
@roles_accepted("rOwner","admin")
def edit_menu_item(restaurant_id, menu_id):
    access = authenticate_session()
    if access: #Admin or Restaurant Owner only
        edited_restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
        edited_item = db.session.query(menu_item).filter_by(id = menu_id).one()
        if edited_item.restaurant_id == edited_restaurant.id:
            if (current_user.restaurant == edited_restaurant.name) or (current_user.restaurant == "admin"):
                if request.method == 'POST':
                    if request.form['name']:
                        edited_item.name = request.form['name']
                    if request.form['description']:
                        edited_item.description = request.form['description']
                    if request.form['price']:
                        edited_item.price = request.form['price']
                    if request.form['course']:
                        edited_item.course = request.form['course']
                    db.session.add(edited_item)
                    db.session.commit() 
                    logging.info(f'{edited_item.name} item edited') 
                    flash('Menu Item Successfully Edited')
                    return redirect(url_for(main_show_menu, restaurant_id = restaurant_id))
                else:
                    return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = edited_item)
            else: 
                flash('You do not own this restaurant!')
                return redirect(url_for('main.show_restaurants'))
        else:
            flash('That Item does not belong to this restaurant')
            return redirect(url_for('main.show_restaurants'))


#Delete a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
@login_required
@roles_accepted("rOwner","admin")
def delete_menu_item(restaurant_id,menu_id):
    item_to_delete = db.session.query(menu_item).filter_by(id = menu_id).one() 
    edited_restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    if item_to_delete.restaurant_id == edited_restaurant.id:
        if (current_user.restaurant == edited_restaurant.name) or (current_user.restaurant == "admin"):
            if request.method == 'POST':
                db.session.delete(item_to_delete)
                db.session.commit()
                logging.info(f'{item_to_delete} item deleted') 
                flash('Menu Item Successfully Deleted')
                return redirect(url_for(main_show_menu, restaurant_id = restaurant_id))
            else:
                return render_template('delete_menu_item.html', item = item_to_delete)
        else: 
            flash('You do not own this restaurant!')
            return redirect(url_for('main.show_restaurants'))
    else:
        flash('That Item does not belong to this restaurant')
        return redirect(url_for('main.show_restaurants'))    



@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
