import os

from flask import Blueprint, jsonify, render_template, request, url_for
from werkzeug import secure_filename
from flask.ext.login import login_required

import db
from util import config, get_logger
logger = get_logger(__name__)


edit_module = Blueprint('edit', __name__)


@edit_module.route('/<user_name>/album/<album_title>/edit/')
@login_required
def index(user_name, album_title):
    logger.debug('{Edit album} %s/album/%s/', user_name, album_title)
    env = {
        'module': 'Edit %s/%s' % (user_name, album_title),
        'album_title': album_title
    }
    return render_template('edit.html', **env)


@edit_module.route('/<user_name>/album/<album_title>/edit/get_items/')
@login_required
def get_items(user_name, album_title):
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
        'image': url_for('static', filename=item.image),
        'description': item.description,
        'ts': item.ts
    } for item in items}
    return jsonify(result)


@edit_module.route('/<user_name>/album/<album_title>/edit/save_items/', methods=['POST'])
@login_required
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
                              ts = %(ts)s
                        WHERE id_item=%(key)s''',
                    {'key': key, 'desc': item['description'], 'ts': item['ts']}
                )
            except:
                return False

    return True


@edit_module.route('/<user_name>/album/<album_title>/edit/upload/', methods=['GET', 'POST'])
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

        uid = db.query_one(cur, 'SELECT id_user FROM travel_log.user WHERE user_name=%(name)s;', {'name': user_name})
        aid = db.query_one(
            cur,
            'SELECT id_album FROM travel_log.album WHERE fk_user = %(uid)s AND album_title = %(album)s AND NOT is_deleted',
            {'uid': uid.id_user, 'album': album_title}
        )

        # Create item in database
        path = os.path.join(
            config['storage-engine']['path'],
            str(uid.id_user), str(aid.id_album))
        if not os.path.isdir(path):
            os.makedirs(path)
        file = os.path.join(path, secure_filename(image.filename))

        url = os.path.join(
            config['storage-engine']['url'],
            str(uid.id_user), str(aid.id_album),
            secure_filename(image.filename)
        )
        cur.execute(
            'INSERT INTO travel_log.item (fk_album, image) VALUES (%(aid)s, %(path)s)',
            {'aid': aid.id_album, 'path': url}
        )

        # Store image in file system
        image.save(file)

    return True
