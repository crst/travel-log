from flask import Blueprint, escape, redirect, render_template, url_for
from flask.ext.login import current_user, login_required

from util import config
import db
from util import get_logger
logger = get_logger(__name__)


user_module = Blueprint('user', __name__)


@user_module.route('/user/<user_name>/')
def index(user_name):
    logger.debug('{User} user/%s', user_name)
    is_current_user = not current_user.is_anonymous and user_name == current_user.name

    albums = get_albums(user_name)

    env = {
        'module': 'User | %s' % escape(user_name),
        'is_current_user': is_current_user,
        'header': True,
        'user': user_name,
        'albums': albums
    }
    return render_template('user.html', **env)



def get_albums(user_name):
    albums = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            albums = db.query_all(
                cur,
                '''
SELECT
  a.id_album, a.album_title, a.album_desc
FROM travel_log.album a
JOIN travel_log.user u ON u.id_user = a.fk_user
WHERE u.user_name=%(user)s AND NOT a.is_deleted
''',
                {'user': user_name})
    return albums
