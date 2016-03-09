import json

from flask import Blueprint, abort, jsonify, flash, render_template, redirect, request, url_for
from flask.ext.login import current_user, login_required

from auth import is_allowed
from common import get_user_id, load_items, load_album, ssl_required
import db
from storage import store_background_fs, store_item_fs
from util import config, get_logger, log_request
logger = get_logger(__name__)


edit_module = Blueprint('edit', __name__)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/')
@login_required
@ssl_required
def index(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{Edit album} %s/album/%s/', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    env = {
        'module': 'Edit %s/%s' % (user_name, album_title),
        'user_name': user_name,
        'album_title': album_title
    }
    return render_template('edit.html', **env)



@edit_module.route('/user/<user_name>/album/<album_title>/edit/get_items/')
@login_required
@ssl_required
def get_items(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{Edit album} %s/album/%s/get_items', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({})

    return load_items(current_user, user_name, album_title)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/get_album/')
@login_required
@ssl_required
def get_album(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{Edit album} %s/album/%s/get_album', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({})

    return load_album(current_user, user_name, album_title)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/save_album/', methods=['POST'])
@login_required
@ssl_required
def save_album(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{Edit album} %s/album/%s/save_album', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({'success': False})

    result = False
    if request.method == 'POST':
        result = store_album(user_name, album_title, request.get_json())

    return jsonify({'success': result})


@edit_module.route('/user/<user_name>/album/<album_title>/edit/save_items/', methods=['POST'])
@login_required
@ssl_required
def save_items(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{Edit album} %s/album/%s/save_items', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({'success': False})

    result = False
    if request.method == 'POST':
        result = store_items(user_name, album_title, request.get_json())

    return jsonify({'success': result})


def store_album(user_name, album_title, album):
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
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
            logger.debug(e)
            return False
    return True


def store_items(user_name, album_title, items):
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            return False

        for key, item in items.items():
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
                        'ts': item['ts'] or None
                    }
                )
            except Exception as e:
                logger.debug(e)
                return False

    return True


@edit_module.route('/user/<user_name>/album/<album_title>/edit/set-item-visibility/', methods=['GET', 'POST'])
@login_required
@ssl_required
def set_item_visibility(user_name, album_title):
    log_request(request, current_user)
    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        data = json.loads(request.data)
        id_item = 'item-id' in data and data['item-id'] or None
        item_visibility = None
        if 'item-visibility' in data:
            item_visibility = data['item-visibility']

        result = set_item_visibility(user_name, album_title, id_item, item_visibility)
        return jsonify({'success': result})

def set_item_visibility(user_name, album_title, id_item, item_visibility):
    if id_item is None or item_visibility is None:
        return False

    id_user = get_user_id(user_name)
    with db.pg_connection(config['app-database']) as (_, cur, _):
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

    return True


@edit_module.route('/user/<user_name>/album/<album_title>/edit/upload_album_background/', methods=['GET', 'POST'])
@login_required
@ssl_required
def upload_background(user_name, album_title):
    log_request(request, current_user)
    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        f = request.files['file']
        result = store_background(f, user_name, album_title)
        return jsonify({'success': result})

def store_background(image, user_name, album_title):
    if config['storage-engine']['type'] == 'filesystem':
        return store_background_fs(image, user_name, album_title)
    return False

@edit_module.route('/user/<user_name>/album/<album_title>/edit/upload_item/', methods=['GET', 'POST'])
@login_required
@ssl_required
def upload_image(user_name, album_title):
    log_request(request, current_user)
    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        f = request.files['file']
        result = store_image(f, user_name, album_title)
        return jsonify({'success': result})


# TODO: add other storage engines here
def store_image(image, user_name, album_title):
    if config['storage-engine']['type'] == 'filesystem':
        return store_item_fs(image, user_name, album_title)
    return False


@edit_module.route('/user/<user_name>/album/<album_title>/edit/delete/<id_item>', methods=['GET', 'POST'])
@login_required
@ssl_required
def delete_item(user_name, album_title, id_item):
    log_request(request, current_user)
    logger.debug('{Edit} %s/%s/delete-item/%s', user_name, album_title, id_item)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        result = delete_one_item(get_user_id(user_name), album_title, id_item)
        if result['success']:
            if result['success']:
                flash('Successfully deleted item')
                return redirect(url_for('edit.index', user_name=user_name, album_title=album_title))
            else:
                flash('Can\'t delete item!')

    env = {
        'user_name': user_name,
        'album_title': album_title,
        'id_item': id_item
    }
    return render_template('item_delete.html', **env)

def delete_one_item(id_user, album_title, id_item):
    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            # We only flag items as deleted here, some worker queue
            # will actually delete them asynchronously.
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
