from functools import wraps

from flask import current_app, jsonify, request, redirect, url_for

import db
from util import config


def get_user_id(user_name):
    result = None
    with db.pg_connection(config['app-database']) as (_, cur, _):
        user = db.query_one(
            cur,
            '''
SELECT id_user
  FROM travel_log.user
 WHERE user_name = %(user)s
            ''',
            {'user': user_name}
        )
        result = user.id_user
    return result



def load_items(current_user, user_name, album_title, only_visible=False):
    visible = (True, False)
    if only_visible:
        visible = (True,)

    with db.pg_connection(config['app-database']) as (_, cur, err):
        items = db.query_all(
            cur,
            '''
SELECT * FROM travel_log.item i
JOIN travel_log.album A ON a.id_album = i.fk_album
JOIN travel_log.user u ON u.id_user = a.fk_user
WHERE u.user_name = %(user)s AND a.album_title = %(album)s
  AND NOT i.is_deleted
  AND NOT a.is_deleted
  AND i.is_visible IN %(visible)s
ORDER BY i.ts
            ''',
            {'user': user_name, 'album': album_title, 'visible': visible}
        )
    result = {'items': [{
        'id': item.id_item,
        'is_visible': item.is_visible,
        'image': url_for('image.images', filename=item.image),
        'description': item.description,
        'lat': str(item.lat),
        'lon': str(item.lon),
        'zoom': item.zoom,
        'ts': item.ts
    } for item in items]}
    return jsonify(result)


def load_album(current_user, user_name, album_title):
    with db.pg_connection(config['app-database']) as (_, cur, _):
        album = db.query_one(
            cur,
            '''
SELECT *
FROM travel_log.album a
JOIN travel_log.user u ON u.id_user = a.fk_user
WHERE u.user_name = %(user)s AND a.album_title = %(album)s
  AND NOT a.is_deleted
            ''',
            {'user': user_name, 'album': album_title}
        )

    if album:
        return jsonify({
            'description': album.album_desc,
            'background': album.background,
            'autoplay_delay': album.autoplay_delay
        })

    return jsonify({})


def ssl_required(f):
    @wraps(f)
    def g(*args, **kwargs):
        if request.is_secure:
            return f(*args, **kwargs)
        return redirect(request.url.replace("http://", "https://"))
    return g
