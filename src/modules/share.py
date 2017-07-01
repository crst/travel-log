import hashlib
import random
import string
import time

import shared.db as db
from shared.util import config, get_logger

logger = get_logger(__name__)


def share_album(user_name, album_title, share):
    logger.debug('{Module|Share} share_album(%s, %s, %s)', user_name, album_title, share)

    if share == 'Hidden':
        m = '%s%s' % (time.time(), ''.join([string.ascii_letters[random.randint(0, len(string.ascii_letters) - 1)] for _ in range(8)]))
        secret = hashlib.sha256(m).hexdigest()
    else:
        secret = None

    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
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
            success = True
        except Exception as e:
            logger.error(e)

    return {'success': success, 'secret': secret, 'msg': 'Changed share type to %s' % share}


def get_share_type(user_name, album_title):
    logger.debug('{Module|Share} get_share_type(%s, %s)', user_name, album_title)

    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
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
        except Exception as e:
            logger.error(e)

    if share_type and share_type.share_type_name:
        return share_type.share_type_name

    return 'Private'


def get_share_types():
    logger.debug('{Module|Share} get_share_types()')

    share_types = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
            share_types = db.query_all(
                cur,
                'SELECT share_type_name FROM travel_log.share_type',
                {}
            )
        except Exception as e:
            logger.error(e)

    return [s.share_type_name for s in share_types]
