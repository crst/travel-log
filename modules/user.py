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

    # TODO: need a better abstraction to get all "allowed" albums
    is_current_user = not current_user.is_anonymous and user_name == current_user.name
    albums = get_albums(user_name, is_current_user)

    env = {
        'module': 'User | %s' % escape(user_name),
        'is_current_user': is_current_user,
        'header': True,
        'user': user_name,
        'albums': albums
    }
    return render_template('user.html', **env)



def get_albums(user_name, is_current_user):
    albums = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        public = not is_current_user and ('Public',) or ('Public', 'Private')
        if not err:
            albums = db.query_all(
                cur,
                '''
SELECT
  a.id_album, a.album_title, a.album_desc, st.share_type_name
FROM travel_log.album a
JOIN travel_log.user u ON u.id_user = a.fk_user
JOIN travel_log.share s ON s.fk_album = a.id_album AND s.fk_user = u.id_user
JOIN travel_log.share_type st ON st.id_share_type = s.fk_share_type
WHERE u.user_name=%(user)s AND NOT a.is_deleted AND st.share_type_name IN %(public)s
''',
                {'user': user_name, 'public': public})
    return albums
