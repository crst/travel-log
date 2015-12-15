from util import get_logger
logger = get_logger(__name__)

from flask import Blueprint, render_template

album_module = Blueprint('album', __name__)


@album_module.route('/<username>/album/<title>/')
def index(username, title):
    logger.debug('{Album} %s/album/%s', username, title)
    env = {
        'module': 'Album',
        'username': username,
        'title': title
    }
    return render_template('album.html', **env)
