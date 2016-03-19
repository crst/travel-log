import shared.db as db
from shared.util import config, get_logger

logger = get_logger(__name__)


def create_new_album(id_user, album_title, album_desc):
    logger.debug('{Modules|Album} create_new_album(%s, %s, %s)', id_user, album_title, album_desc)

    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
            album = db.query_one(
                cur,
                'SELECT id_album FROM travel_log.album WHERE album_title = %(album)s and fk_user = %(user)s AND NOT is_deleted;',
                {'album': album_title, 'user': id_user})
            if not album.id_album:
                cur.execute(
                    'INSERT INTO travel_log.album (album_title, album_desc, fk_user) VALUES (%(title)s, %(desc)s, %(user)s);',
                    {'title': album_title, 'desc': album_desc, 'user': id_user})

                cur.execute('''
INSERT INTO travel_log.share (fk_album, fk_share_type, fk_user)
  SELECT
    id_album,
    id_share_type,
     %(user)s
  FROM travel_log.album a
  CROSS JOIN travel_log.share_type st
  WHERE a.fk_user = %(user)s
    AND a.album_title = %(title)s
    AND st.share_type_name = \'Private\'
                ''',
                {'title': album_title, 'user': id_user})
                success = True
        except Exception as e:
            logger.error(e)

    return {'success': success}


def delete_one_album(id_user, album_title):
    logger.debug('{Module|Album} delete_one_album(%s, %s)', id_user, album_title)

    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
            # We only flag album as deleted here, some worker queue
            # will actually delete them (and cascade to items).
            cur.execute(
                '''
UPDATE travel_log.album
SET is_deleted = TRUE
WHERE fk_user=%(user)s AND album_title=%(album)s
                ''',
                {'user': id_user, 'album': album_title}
            )
            success = True
        except Exception as e:
            logger.error(e)

    return {'success': success}
