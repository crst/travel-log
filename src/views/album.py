from flask import Blueprint, abort, escape, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from shared.auth import is_allowed, is_shared
from shared.common import get_user_id, load_items, load_album, ssl_required
from shared.util import get_logger, log_request
from modules.album import create_new_album, delete_one_album

logger = get_logger(__name__)
album_module = Blueprint('album', __name__)


@album_module.route('/user/<user_name>/album/<album_title>/view/')
@album_module.route('/user/<user_name>/album/<album_title>/<secret_part>/view/')
def index(user_name, album_title, secret_part=None):
    log_request(request, current_user)
    logger.debug('{View|Album} index(%s, %s, %s)', user_name, album_title, secret_part)

    shared = is_shared(current_user, user_name, album_title, secret_part)
    if not shared:
        return abort(404)

    env = {
        'module': '%s | %s' % (user_name, album_title),
        'header': False,
        'user': user_name,
        'album_title': album_title,
    }
    return render_template('album.html', **env)


@album_module.route('/user/<user_name>/album/<album_title>/view/get_items/')
@album_module.route('/user/<user_name>/album/<album_title>/<secret_part>/view/get_items/')
def get_items(user_name, album_title, secret_part=None):
    log_request(request, current_user)
    logger.debug('{View|Album} get_items(%s, %s, %s)', user_name, album_title, secret_part)

    if not is_shared(current_user, user_name, album_title, secret_part):
        return jsonify({})

    return load_items(user_name, album_title, only_visible=True)


@album_module.route('/user/<user_name>/album/<album_title>/view/get_album/')
@album_module.route('/user/<user_name>/album/<album_title>/<secret_part>/view/get_album/')
def get_album(user_name, album_title, secret_part=None):
    log_request(request, current_user)
    logger.debug('{View|Album} get_album(%s, %s, %s)', user_name, album_title, secret_part)

    if not is_shared(current_user, user_name, album_title, secret_part):
        return jsonify({})

    return load_album(current_user, user_name, album_title)


@album_module.route('/user/<user_name>/album/new', methods=['GET', 'POST'])
@login_required
@ssl_required
def new_album(user_name):
    log_request(request, current_user)
    logger.debug('{View|Album} new_album(%s)', user_name)

    if not is_allowed(current_user, user_name):
        return redirect(url_for('album.new_album', user_name=current_user.name))

    if request.method == 'POST':
        album_title = 'album_title' in request.form and escape(request.form['album_title']) or 'No title'
        album_desc = 'album_desc' in request.form and escape(request.form['album_desc']) or 'No description'
        result = create_new_album(get_user_id(user_name), album_title, album_desc)
        if result['success']:
            flash('Successfully created new album "%s"' % album_title, 'success')
            return redirect(url_for('user.index', user_name=user_name))
        else:
            flash('Can\'t create new album "%s"' % album_title, 'danger')

    env = {
        'module': 'Create new album',
        'header': True,
    }
    return render_template('album_new.html', **env)


@album_module.route('/user/<user_name>/album/<album_title>/delete/', methods=['GET', 'POST'])
@login_required
@ssl_required
def delete_album(user_name, album_title):
    log_request(request, current_user)
    logger.debug('{View|Album} delete_album(%s, %s)', user_name, album_title)

    if not is_allowed(current_user, user_name):
        return abort(404)

    if request.method == 'POST':
        result = delete_one_album(get_user_id(user_name), album_title)
        if result['success']:
            if result['success']:
                flash('Successfully deleted album "%s"' % album_title, 'success')
                return redirect(url_for('user.index', user_name=user_name))
            else:
                flash('Can\'t delete album "%s"' % album_title, 'danger')

    env = {
        'user_name': user_name,
        'album_title': album_title,
    }
    return render_template('album_delete.html', **env)
