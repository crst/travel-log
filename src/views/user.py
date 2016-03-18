from flask import Blueprint, escape, render_template, request
from flask.ext.login import current_user

from shared.common import is_current_user
from shared.util import get_logger, log_request
from modules.user import get_albums

logger = get_logger(__name__)
user_module = Blueprint('user', __name__)


@user_module.route('/user/<user_name>/')
def index(user_name):
    log_request(request, current_user)
    logger.debug('{View|User} index(%s)', user_name)

    albums = get_albums(user_name, current_user)

    env = {
        'module': 'User | %s' % escape(user_name),
        'is_current_user': is_current_user(user_name, current_user),
        'header': True,
        'user': user_name,
        'albums': albums,
    }
    return render_template('user.html', **env)
