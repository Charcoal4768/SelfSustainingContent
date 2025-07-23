from . import db
from flask import Blueprint, render_template, redirect, url_for

views = Blueprint('views',__name__)

@views.route('/')
def MainPage():
    return render_template('home.html')