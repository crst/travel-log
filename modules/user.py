from flask import Blueprint, redirect, render_template, url_for
from flask.ext.login import current_user, login_required

from util import config
import db
from util import get_logger
logger = get_logger(__name__)


user_module = Blueprint('user', __name__)


@user_module.route('/user/<user_name>/')
@login_required
def index(user_name):
    logger.debug('{User} user/%s', user_name)
    if user_name != current_user.name:
        return redirect(url_for('user.index', user_name=current_user.name))

    albums = get_albums(current_user.id_user)

    env = {
        'module': 'User',
        'header': True,
        'albums': albums
    }
    return render_template('user.html', **env)



def get_albums(id_user):
    albums = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            albums = db.query_all(
                cur,
                'SELECT id_album, album_title FROM travel_log.album WHERE fk_user=%(user)s AND NOT is_deleted',
                {'user': id_user})
    return albums
