from flask import Blueprint, abort, escape, flash, render_template, redirect, request, url_for
from flask.ext.login import current_user, login_required

from shared.auth import is_allowed
from shared.util import get_logger, log_request
from modules.share import share_album, get_share_type, get_share_types

logger = get_logger(__name__)
share_module = Blueprint('share', __name__)


@share_module.route('/user/<user_name>/album/<album_title>/share/', methods=['GET', 'POST'])
@login_required
def index(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Share} index(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        share_type = 'share_type' in request.form and escape(request.form['share_type']) or 'Private'
        result = share_album(user_name, album_title, share_type)
        flash(result['msg'], 'info')
        return redirect(url_for('user.index', user_name=user_name))

    env = {
        'module': 'Share album',
        'title': album_title,
        'share_type': get_share_type(escape(user_name), escape(album_title)),
        'share_types': get_share_types()
    }
    return render_template('share.html', **env)
