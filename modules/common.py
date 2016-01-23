from flask import jsonify, url_for

import db
from util import config


def check_auth(current_user, user_name, album_title):
    if not current_user.is_anonymous and current_user.name == user_name:
        return True

    with db.pg_connection(config['app-database']) as (_, cur, err):
        share_type = db.query_one(
            cur,
            '''
SELECT
  st.share_type_name
FROM travel_log.share s
JOIN travel_log.share_type st ON st.id_share_type = s.fk_share_type
JOIN travel_log.album a ON a.id_album = s.fk_album
JOIN travel_log.user u ON u.id_user = s.fk_user
WHERE a.album_title = %(album)s
  AND u.user_name = %(user)s
''',
            {'user': user_name, 'album': album_title}
        )
        if share_type.share_type_name == 'Public':
            return True

    return False


def load_items(current_user, user_name, album_title):
    if not check_auth(current_user, user_name, album_title):
        return jsonify({})

    with db.pg_connection(config['app-database']) as (_, cur, err):
        items = db.query_all(
            cur,
            '''
            SELECT * FROM travel_log.item i
            JOIN travel_log.album A ON a.id_album = i.fk_album
            JOIN travel_log.user u ON u.id_user = a.fk_user
            WHERE u.user_name = %(user)s AND a.album_title = %(album)s
            ''',
            {'user': user_name, 'album': album_title}
        )
    result = {item.id_item: {
        'image': url_for('image.images', filename=item.image),
        'description': item.description,
        'ts': item.ts
    } for item in items}
    return jsonify(result)
