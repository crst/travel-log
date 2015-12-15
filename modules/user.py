from util import get_logger
logger = get_logger(__name__)

from flask import Blueprint, render_template

user_module = Blueprint('user', __name__)


@user_module.route('/<username>/')
def index(username):
    logger.debug('{User} user/%s', username)
    env = {
        'module': 'User',
        'username': username,
    }
    return render_template('user.html', **env)
