from flask import render_template, session
from Resort.main import main
from functools import wraps
from flask_login import  current_user


@main.route('/')
def index():
    name = None
    welcome_message = None
    if current_user.is_authenticated:
        name = current_user.name
        
        if 'show_welcome' in session:
            welcome_message = True
            session.pop('show_welcome', None)
    return render_template('index.html', name=name, welcome_message=welcome_message,title='Home')

@main.route('/about')
def about():
    return render_template('about.html', title='About')