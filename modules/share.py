from util import get_logger
logger = get_logger(__name__)

from flask import Blueprint, render_template

share_module = Blueprint('share', __name__)


@share_module.route('/<user_name>/album/<album_title>/share/')
def index(user_name, album_title):
    logger.debug('{Share album} %s/album/%s', user_name, album_title)
    env = {
        'module': 'Share album',
        'title': album_title
    }
    return render_template('share.html', **env)
