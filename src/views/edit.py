import json

from flask import Blueprint, abort, jsonify, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required

from shared.auth import is_allowed
from shared.common import get_user_id, load_items, load_album, ssl_required
from shared.util import get_logger, log_request
from modules.edit import store_album, store_items, change_item_visibility, store_background, store_image, delete_one_item

logger = get_logger(__name__)
edit_module = Blueprint('edit', __name__)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/')
@login_required
@ssl_required
def index(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} index(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    env = {
        'module': 'Edit %s/%s' % (user_name, album_title),
        'user_name': user_name,
        'album_title': album_title,
    }
    return render_template('edit.html', **env)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/get_items/')
@login_required
@ssl_required
def get_items(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} get_items(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({})

    return load_items(user_name, album_title)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/get_album/')
@login_required
@ssl_required
def get_album(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} get_album(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({})

    return load_album(current_user, user_name, album_title)


@edit_module.route('/user/<user_name>/album/<album_title>/edit/save_album/', methods=['POST'])
@login_required
@ssl_required
def save_album(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} save_album(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({'success': False})

    result = False
    if request.method == 'POST':
        data = request.get_json()
        del data['_csrf_token']
        result = store_album(user_name, album_title, data)

    return jsonify({'success': result})


@edit_module.route('/user/<user_name>/album/<album_title>/edit/save_items/', methods=['POST'])
@login_required
@ssl_required
def save_items(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} save_items(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return jsonify({'success': False})

    result = False
    if request.method == 'POST':
        data = request.get_json()
        del data['_csrf_token']
        result = store_items(user_name, album_title, data)

    return jsonify({'success': result})


@edit_module.route('/user/<user_name>/album/<album_title>/edit/set-item-visibility/', methods=['GET', 'POST'])
@login_required
@ssl_required
def set_item_visibility(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} set_item_visibility(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        data = json.loads(request.data)
        id_item = data['item-id'] if 'item-id' in data else None
        item_visibility = data['item-visibility'] if 'item-visibility' in data else None
        result = change_item_visibility(user_name, album_title, id_item, item_visibility)
        return jsonify({'success': result})


@edit_module.route('/user/<user_name>/album/<album_title>/edit/upload_album_background/', methods=['GET', 'POST'])
@login_required
@ssl_required
def upload_background(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} upload_background(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        f = request.files['file']
        result = store_background(f, user_name, album_title)
        return jsonify({'success': result})


@edit_module.route('/user/<user_name>/album/<album_title>/edit/upload_item/', methods=['GET', 'POST'])
@login_required
@ssl_required
def upload_image(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Edit} upload_image(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        f = request.files['file']
        result = store_image(f, user_name, album_title)
        return jsonify({'success': result})


@edit_module.route('/user/<user_name>/album/<album_title>/edit/delete/<id_item>', methods=['GET', 'POST'])
@login_required
@ssl_required
def delete_item(user_name, album_title, id_item):
    log_request(request, current_user)
    logger.debug('{View|Edit} delete_item(%s, %s, %s)', user_name, album_title, id_item)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        result = delete_one_item(get_user_id(user_name), album_title, id_item)
        if result['success']:
            if result['success']:
                flash('Successfully deleted item', 'success')
                return redirect(url_for('edit.index', user_name=user_name, album_title=album_title))
            else:
                flash('Can\'t delete item!', 'danger')

    env = {
        'user_name': user_name,
        'album_title': album_title,
        'id_item': id_item
    }
    return render_template('item_delete.html', **env)
