import hashlib
import random
import string
import time

from flask import Blueprint, abort, escape, flash, render_template, redirect, request, url_for
from flask.ext.login import current_user, login_required

from auth import is_allowed
import db
from util import config, get_logger
logger = get_logger(__name__)


share_module = Blueprint('share', __name__)


@share_module.route('/user/<user_name>/album/<album_title>/share/', methods=['GET', 'POST'])
@login_required
def index(user_name, album_title):
    logger.debug('{Share album} %s/album/%s', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        share_type = 'share_type' in request.form and escape(request.form['share_type']) or 'Private'
        result = share_album(user_name, album_title, share_type)
        flash(result['msg'])
        return redirect(url_for('user.index', user_name=user_name))

    env = {
        'module': 'Share album',
        'title': album_title,
        'share_type': get_share_type(escape(user_name), escape(album_title)),
        'share_types': get_share_types()
    }
    return render_template('share.html', **env)


def share_album(user_name, album_title, share):
    if share == 'Hidden':
        m = '%s%s' % (time.time(), ''.join([string.ascii_letters[random.randint(0, len(string.ascii_letters) - 1)] for _ in range(8)]))
        secret = hashlib.sha256(m).hexdigest()
    else:
        secret = None

    with db.pg_connection(config['app-database']) as (_, cur, err):
        cur.execute('''
UPDATE travel_log.share
   SET fk_share_type = share_type.id_share_type,
       secret = %(secret)s
FROM travel_log.album,
     travel_log.user,
     travel_log.share_type
WHERE album.id_album = share.fk_album AND album.album_title = %(album)s
  AND NOT album.is_deleted
  AND "user".id_user = share.fk_user AND "user".user_name = %(user)s
  AND share_type.share_type_name = %(share)s
''',
                    {'user': user_name, 'album': album_title, 'share': share, 'secret': secret})
    return {'success': True, 'secret': secret, 'msg': 'Changed share type to %s' % share}


def get_share_type(user_name, album_title):
    with db.pg_connection(config['app-database']) as (_, cur, err):
        share_type = db.query_one(
            cur,
            '''
SELECT
  st.share_type_name
FROM travel_log.share s
JOIN travel_log.share_type st ON st.id_share_type = s.fk_share_type
JOIN travel_log.user u ON u.id_user = s.fk_user
JOIN travel_log.album a ON a.id_album = s.fk_album
WHERE u.user_name = %(user)s AND a.album_title = %(album)s
  AND NOT a.is_deleted
            ''',
            {'user': user_name, 'album': album_title}
        )
    return share_type.share_type_name


def get_share_types():
    with db.pg_connection(config['app-database']) as (_, cur, err):
        share_types = db.query_all(
            cur,
            'SELECT share_type_name FROM travel_log.share_type',
            {}
        )
    return [s.share_type_name for s in share_types]
