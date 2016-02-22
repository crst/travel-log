from flask import Blueprint, escape, redirect, render_template, url_for
from flask.ext.login import current_user, login_required

from auth import is_shared
from common import is_current_user
import db
from util import config, get_logger
logger = get_logger(__name__)


user_module = Blueprint('user', __name__)


@user_module.route('/user/<user_name>/')
def index(user_name):
    logger.debug('{User} user/%s', user_name)

    albums = get_albums(user_name, current_user)

    env = {
        'module': 'User | %s' % escape(user_name),
        'is_current_user': is_current_user(user_name, current_user),
        'header': True,
        'user': user_name,
        'albums': albums
    }
    return render_template('user.html', **env)



def get_albums(user_name, current_user):
    albums = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            albums = db.query_all(
                cur,
                '''
SELECT
  a.id_album, a.album_title, a.album_desc, st.share_type_name, s.secret
FROM travel_log.album a
JOIN travel_log.user u ON u.id_user = a.fk_user
JOIN travel_log.share s ON s.fk_album = a.id_album AND s.fk_user = u.id_user
JOIN travel_log.share_type st ON st.id_share_type = s.fk_share_type
WHERE u.user_name=%(user)s AND NOT a.is_deleted
                ''',
                {'user': user_name})

    result = [a for a in albums if is_shared(current_user, user_name, a.album_title, None)]
    return result
