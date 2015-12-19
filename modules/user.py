from flask import Blueprint, redirect, render_template, url_for
from flask.ext.login import current_user, login_required

from util import get_logger
logger = get_logger(__name__)


user_module = Blueprint('user', __name__)


@user_module.route('/user/<username>/')
@login_required
def index(username):
    logger.debug('{User} user/%s', username)
    if username != current_user.name:
        return redirect(url_for('user.index', username=current_user.name))
    env = {
        'module': 'User',
        'username': username,
    }
    return render_template('user.html', **env)
