from . import db
from flask import Blueprint, render_template, redirect, url_for, request
from .generator import SearchTermsPrompt
from .generator.controller import startProcess

views = Blueprint('views',__name__)

@views.route('/')
def MainPage():
    return render_template('home.html')

@views.route('/create', methods=['GET', 'POST'])
def Adminpanel():
    '''Hookup to generator'''
    if request.method == 'POST':
        product1 = request.form.get('product1')
        product2 = request.form.get('product2')
        affiliate1 = request.form.get('affiliate1')
        affiliate2 = request.form.get('affiliate2')
        extra = request.form.get('extra')
        prompt = SearchTermsPrompt(product1=product1, product2=product2, extra_txt=extra)
        startProcess(prompt)
    return render_template('admin.html')