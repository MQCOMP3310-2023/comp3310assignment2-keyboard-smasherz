from flask import Blueprint, render_template, request, flash, redirect, url_for, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from flask_security import roles_accepted
from .models import user, role, UserRoles
from . import db
from flask_login import login_user
import re

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
        flash('Please check your login details and try again.')
        return redirect(url_for('main.show_restaurants'))
    login_user(User)
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
        flash('Email address already exists')
        return redirect(url_for('main.show_restaurants'))

    public_role = role(name='public')

    new_user = user(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.show_restaurants'))


@auth.route('/add', methods=['GET'])
# @login_required
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

    User = user.query.filter_by(email=email).first()

    if User:
        flash('Email address already exists')
        return redirect(url_for('main.show_restaurants'))
    
    role = role(name=role)

    new_user = user( email=email, name=name, password=generate_password_hash(password, method='sha256'))


    db.session.add(new_user)
    db.session.commit()

    new_user.roles[role]

    return redirect(url_for('auth.login'))
