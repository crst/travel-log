from util import get_logger
logger = get_logger(__name__)

from flask import Blueprint, render_template

share_module = Blueprint('share', __name__)


@share_module.route('/<username>/album/<title>/share/')
def index(username, title):
    logger.debug('{Share album} %s/album/%s', username, title)
    env = {
        'module': 'Share album',
        'username': username,
        'title': title
    }
    return render_template('share.html', **env)
