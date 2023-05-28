from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import user
from . import db
from flask_login import login_user

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

    User = user.query.filter_by(email=email).first()

    if User:
        flash('Email address already exists')
        return redirect(url_for('main.show_restaurants'))

    new_user = user(role='public', email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.show_restaurants'))


