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

    albums = get_albums(current_user.name)

    env = {
        'module': 'User',
        'header': True,
        'albums': albums
    }
    return render_template('user.html', **env)


# TODO: move function to somewhere else?
def get_albums(user_name):
    albums = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            user = db.query_one(cur, 'SELECT id_user FROM app.user WHERE user_name=%(name)s;', {'name': user_name})
            albums = db.query_all(
                cur,
                'SELECT id_album, album_title FROM app.album WHERE fk_user=%(user)s',
                {'user': user.id_user})
    return albums
