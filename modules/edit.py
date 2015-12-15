from util import get_logger
logger = get_logger(__name__)

from flask import Blueprint, render_template

edit_module = Blueprint('edit', __name__)

@edit_module.route('/<username>/album/<title>/edit/')
def index(username, title):
    logger.debug('{Edit album} %s/album/%s/', username, title)
    env = {
        'module': 'Edit album',
        'username': username,
        'title': title
    }
    return render_template('edit.html', **env)
