from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Users
from . import db
from .forms import LoginForm, SignupForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.MainPage'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.get_user_by_email(form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('views.MainPage'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form, current_user=current_user)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.MainPage'))

    form = SignupForm()
    try:
        if form.validate_on_submit():
            if Users.get_user_by_email(form.email.data):
                flash('Email already registered.', 'warning')
            else:
                hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
                user = Users.make_user(form.email.data, hashed_pw, form.username.data)
                login_user(user)
                return redirect(url_for('views.MainPage'))
    except Exception as e:
        print("Signup Failed:",e)
        raise e
    return render_template('signup.html', form=form, current_user=current_user)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
