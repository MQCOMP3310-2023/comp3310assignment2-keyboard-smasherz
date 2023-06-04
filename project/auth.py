from flask import current_app, Blueprint, render_template, request, flash, redirect, url_for, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_security import roles_accepted, Security
from .models import user, Role, user_roles
from . import db
from flask_login import login_user
import re
import logging

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    User = user.query.filter_by(email=email).first()
    if not User or not check_password_hash(User.password, password):
        logging.error(f'{email} login failed ')
        flash('Please check your Credentials and try again.')
        return redirect(url_for('main.show_restaurants'))
    login_user(User)
    logging.info(f'{email} logged in')
    return redirect(url_for('main.profile'))

@auth.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        flash('Invalid email address')
        return redirect(url_for('main.show_restaurants'))
    
    if not re.search("[!@#$%^&*()\-_=+{};:,<.>]", password):
        flash('Password must include at least one special character')
        return redirect(url_for('main.show_restaurants'))

    User = user.query.filter_by(email=email).first()

    if User:
        flash('User/Email already exists')
        logging.error(f'{email} {name} already exists')
        return redirect(url_for('main.show_restaurants'))

    public_role = Role(name='public')

    new_user = user(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    logging.info(f'{new_user.name} {new_user.email} user created')
    db.session.add(new_user)
    db.session.commit()

    new_user.roles = [public_role]

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been Logged out! come back soon :)')
    return redirect(url_for('main.show_restaurants'))


@auth.route('/add', methods=['GET'])
@login_required
@roles_accepted('admin')
def add():
    return render_template('add.html')

@auth.route('/add', methods=['POST'])
@login_required
@roles_accepted('admin')
def admin_post():
    role= request.form.get('role')
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    restaurant = request.form.get('restaurant')

    User = db.session.query(user).filter_by(email=email).one()

    if User:
        if role and (role == 'admin' or role == 'rOwner' or role == 'public'):
            role_obj = db.session.query(Role).filter_by(name=role).one()
            relation_user = db.session.query(user_roles).filter_by(user_id=User.id).one()
            logging.info(f'{User.roles} {role_obj.name} User Role Orginal')
            
            User.roles.append(role_obj)
            db.session.commit()
            logging.info(f'{User.roles} {role_obj} User Role Updated')

        if name:
            User.name = name
            db.session.commit()
        if password:
            User.password = generate_password_hash(password, method='sha256')
            db.session.commit()
        if restaurant:
            logging.info(f'{restaurant} {User.name} Res Orignal')
            User.restaurant = restaurant
            logging.info(f'{User.restaurant} {User.name} User Res Updated')
            db.session.commit()
    
    else: 
        role = db.session.query(Role).filter_by(name=role).one()

        new_user = user(email=email, name=name, password=generate_password_hash(password, method='sha256'), restaurant=restaurant)


        db.session.add(new_user)
        db.session.commit()

        new_user.roles[role]
        db.session.commit()

    return redirect(url_for('auth.login'))
