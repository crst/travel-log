from dateutil.parser import parse as date_parser

import shared.db as db
from shared.util import config, get_logger, log_request
from shared.common import get_user_id
from shared.storage import store_background_fs, store_item_fs

logger = get_logger(__name__)


def store_album(user_name, album_title, album):
    logger.debug('{Modules|Edit} store_album(%s, %s, %s)', user_name, album_title, album)

    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)
            return False

        try:
            cur.execute(
            '''
UPDATE travel_log.album
   SET album_desc = %(description)s,
       autoplay_delay = %(autoplay_delay)s,
       background = CASE WHEN substring(%(background)s, 1, 1) = '#' THEN %(background)s ELSE background END
  FROM travel_log.user
 WHERE album.fk_user = "user".id_user
   AND "user".user_name = %(user)s
   AND album.album_title = %(album)s
   AND NOT album.is_deleted
            ''',
                {
                    'user': user_name,
                    'album': album_title,
                    'description': album['description'],
                    'autoplay_delay': album['autoplay_delay'],
                    'background': album['background']
                }
            )
        except Exception as e:
            logger.error(e)
            return False
    return True


def store_items(user_name, album_title, items):
    logger.debug('{Modules|Edit} store_items(%s, %s)', user_name, album_title)

    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)
            return False

        for key, item in items.items():
            ts = date_parser(item['ts']).strftime('%Y-%m-%d %H:%M:%S')

            try:
                cur.execute(
                    '''
UPDATE travel_log.item
   SET description = %(desc)s,
       lat = %(lat)s,
       lon = %(lon)s,
       zoom = %(zoom)s,
       ts = %(ts)s
  FROM travel_log.album,
       travel_log.user
 WHERE item.fk_album = album.id_album
   AND album.fk_user = "user".id_user
   AND "user".user_name = %(user)s
   AND album.album_title = %(album)s
   AND id_item=%(key)s
   AND NOT album.is_deleted
   AND NOT item.is_deleted
                    ''',
                    {
                        'user': user_name,
                        'album': album_title,
                        'key': key,
                        'desc': item['description'],
                        'lat': item['lat'] != 'None' and item['lat'] or None,
                        'lon': item['lon'] != 'None' and item['lon'] or None,
                        'zoom': item['zoom'] or 12,
                        'ts': ts or None,
                    }
                )
            except Exception as e:
                logger.error(e)
                return False

    return True


def change_item_visibility(user_name, album_title, id_item, item_visibility):
    logger.debug('{Modules|Edit} set_item_visibility(%s, %s, %s, %s)', user_name, album_title, id_item, item_visibility)

    if id_item is None or item_visibility is None:
        return False

    id_user = get_user_id(user_name)
    with db.pg_connection(config['app-database']) as (_, cur, _):
        try:
            cur.execute(
                '''
UPDATE travel_log.item
   SET is_visible = %(visible)s
  FROM travel_log.album
 WHERE item.fk_album = album.id_album
   AND fk_user=%(user)s AND album_title=%(album)s
   AND item.id_item=%(id_item)s
                ''',
                {'user': id_user, 'album': album_title, 'id_item': id_item, 'visible': item_visibility}
            )
        except Exception as e:
            logger.error(e)
            return False

    return True


def store_background(image, user_name, album_title):
    logger.debug('{Modules|Edit} store_background(%s, %s)', user_name, album_title)

    if config['storage-engine']['type'] == 'filesystem':
        return store_background_fs(image, user_name, album_title)
    return False


def store_image(image, user_name, album_title):
    logger.debug('{Modules|Edit} store_image(%s, %s)', user_name, album_title)

    if config['storage-engine']['type'] == 'filesystem':
        return store_item_fs(image, user_name, album_title)
    return False


def delete_one_item(id_user, album_title, id_item):
    logger.debug('{Modules|Edit} delete_one_item(%s, %s, %s)', id_user, album_title, id_item)

    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)
            return False

        # We only flag items as deleted here, some worker queue
        # will actually delete them asynchronously.
        try:
            cur.execute(
                '''
UPDATE travel_log.item
   SET is_deleted = TRUE
  FROM travel_log.album
 WHERE item.fk_album = album.id_album
   AND fk_user=%(user)s AND album_title=%(album)s
   AND item.id_item=%(id_item)s
                ''',
                {'user': id_user, 'album': album_title, 'id_item': id_item}
            )
            success = True
        except Exception as e:
            logger.error(e)

    return {'success': success}
