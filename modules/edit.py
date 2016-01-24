import hashlib
import os
import time

from flask import Blueprint, jsonify, render_template, request
from werkzeug import secure_filename
from flask.ext.login import current_user, login_required

from common import load_items, ssl_required
import db
from util import config, get_logger
logger = get_logger(__name__)


edit_module = Blueprint('edit', __name__)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/')
@login_required
@ssl_required
def index(user_name, album_title):
    logger.debug('{Edit album} %s/album/%s/', user_name, album_title)
    env = {
        'module': 'Edit %s/%s' % (user_name, album_title),
        'album_title': album_title
    }
    return render_template('edit.html', **env)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/get_items/')
@login_required
@ssl_required
def get_items(user_name, album_title):
    return load_items(current_user, user_name, album_title)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/save_items/', methods=['POST'])
@login_required
@ssl_required
def save_items(user_name, album_title):
    result = False
    if request.method == 'POST':
        result = store_items(user_name, album_title, request.get_json())

    return jsonify({'success': result})


def store_items(user_name, album_title, items):
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            return False

        for key, item in items.items():
            # TODO: need to make sure users can only edit their own items
            try:
                cur.execute(
                    '''UPDATE travel_log.item
                          SET description = %(desc)s,
                              lat = %(lat)s,
                              lon = %(lon)s,
                              zoom = %(zoom)s,
                              ts = %(ts)s
                        WHERE id_item=%(key)s''',
                    {
                        'key': key,
                        'desc': item['description'],
                        'lat': item['lat'] != 'None' and item['lat'] or None,
                        'lon': item['lon'] != 'None' and item['lon'] or None,
                        'zoom': item['zoom'] or 12,
                        'ts': item['ts'] or None
                    }
                )
            except Exception as e:
                logger.debug(e)
                return False

    return True


@edit_module.route('/user/<user_name>/album/<album_title>/edit/upload/', methods=['GET', 'POST'])
@login_required
@ssl_required
def upload_image(user_name, album_title):
    if request.method == 'POST':
        file = request.files['file']
        result = store_image(file, user_name, album_title)
        return jsonify({'success': result})


# TODO: add other storage engines here
def store_image(image, user_name, album_title):
    if config['storage-engine']['type'] == 'filesystem':
        return store_fs(image, user_name, album_title)
    return False


# TODO: do this properly
def store_fs(image, user_name, album_title):
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            return False

        uid = current_user.id_user
        aid = db.query_one(
            cur,
            'SELECT id_album FROM travel_log.album WHERE fk_user = %(uid)s AND album_title = %(album)s AND NOT is_deleted',
            {'uid': uid, 'album': album_title}
        )

        # Create item in database
        fs_path = os.path.join(
            config['storage-engine']['path'],
            str(uid), str(aid.id_album))
        if not os.path.isdir(fs_path):
            os.makedirs(fs_path)

        filename = hashlib.sha256(
            '%s-%s-%s-%s' % (uid, aid, time.time(), secure_filename(image.filename))
        ).hexdigest()
        fs_file = os.path.join(fs_path, '%s.jpg' % filename)
        rel_path = os.path.join(str(uid), str(aid.id_album), '%s.jpg' % filename)

        # TODO: either store file and database entry or revert both
        cur.execute(
            'INSERT INTO travel_log.item (fk_album, image) VALUES (%(aid)s, %(image)s)',
            {'aid': aid.id_album, 'image': rel_path}
        )
        # Store image in file system
        image.save(fs_file)

    return True
