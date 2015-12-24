from flask import Blueprint, escape, flash, get_flashed_messages, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_user, logout_user

import db
from util import get_logger
logger = get_logger(__name__)


index_module = Blueprint('index', __name__)


@index_module.route('/')
def index():
    logger.debug('{Index}')

    featured = [
        {'image': 'berlin.jpg', 'caption': 'Berlin', 'description': 'Winter in Berlin. Awesome.'},
        {'image': 'valencia.jpg', 'caption': 'Valencia', 'description': 'Ciudad de las Artes y las Ciencias.'},
        {'image': 'lisbon.jpg', 'caption': 'Lisbon', 'description': 'Amazing city.'},
        {'image': 'barcelona.jpg', 'caption': 'Barcelona', 'description': 'Well, it\'s Barcelona.'},
    ]

    env = {
        'module': 'Home',
        'featured': featured
    }
    return render_template('index.html', **env)


@index_module.route('/login/', methods=['GET', 'POST'])
def login():
    logger.debug('{Login}')
    if current_user.is_authenticated:
        return redirect(url_for('user.index', user_name=current_user.name))

    if request.method == 'POST':
        user_name = 'user_name' in request.form and escape(request.form['user_name']) or ''
        pw = 'password' in request.form and escape(request.form['password']) or ''
        u = db.User(user_name)
        u.set_authenticated(pw)
        if u.is_authenticated():
            login_user(u)
            return redirect(url_for('user.index', user_name=user_name))
        else:
            flash('Login failed!')

    env = {
        'module': 'Login',
        'errors': get_flashed_messages(),
    }
    return render_template('login.html', **env)


@index_module.route('/logout/')
def logout():
    logger.debug('{Logout}')
    logout_user()
    return redirect(url_for('index.index'))
