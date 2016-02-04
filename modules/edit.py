from flask import Blueprint, jsonify, flash, render_template, redirect, request, url_for
from flask.ext.login import current_user, login_required

from common import load_items, ssl_required
import db
from storage import store_fs
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


@edit_module.route('/user/<user_name>/album/<album_title>/edit/delete/<id_item>', methods=['GET', 'POST'])
@login_required
@ssl_required
def delete_item(user_name, album_title, id_item):
    logger.debug('{Edit} %s/%s/delete-item/%s', user_name, album_title, id_item)
    if user_name != current_user.name:
        return redirect(url_for('edit.index', user_name=current_user.name, album_title=album_title))

    if request.method == 'POST':
        result = delete_one_item(current_user.id_user, album_title, id_item)
        if result['success']:
            if result['success']:
                flash('Successfully deleted item')
                return redirect(url_for('edit.index', user_name=current_user.name, album_title=album_title))
            else:
                flash('Can\'t delete item!')

    env = {
        'album_title': album_title,
        'id_item': id_item
    }
    return render_template('item_delete.html', **env)

def delete_one_item(id_user, album_title, id_item):
    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            # We only flag items as deleted here, some worker queue
            # will actually delete them.
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

    return {'success': success}
