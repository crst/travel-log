from util import get_logger
logger = get_logger(__name__)

from flask import Blueprint, render_template

edit_module = Blueprint('edit', __name__)

@edit_module.route('/<user_name>/album/<album_title>/edit/')
def index(user_name, album_title):
    logger.debug('{Edit album} %s/album/%s/', user_name, album_title)
    env = {
        'module': 'Edit album',
        'album_title': album_title
    }
    return render_template('edit.html', **env)
