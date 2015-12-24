
from flask import Blueprint, escape, flash, get_flashed_messages, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_required

from util import config
import db
from util import get_logger
logger = get_logger(__name__)


album_module = Blueprint('album', __name__)



@album_module.route('/user/<user_name>/album/view/<album_title>/')
def index(user_name, album_title):
    logger.debug('{Album} %s/album/%s', user_name, album_title)
    env = {
        'module': 'Album',
        'album_title': album_title
    }
    return render_template('album.html', **env)



@album_module.route('/user/<user_name>/album/new', methods=['GET', 'POST'])
@login_required
def new_album(user_name):
    logger.debug('{Album} %s/new-album', user_name)
    if user_name != current_user.name:
        return redirect(url_for('album.new_album', user_name=current_user.name))

    if request.method == 'POST':
        album_title = 'album_title' in request.form and escape(request.form['album_title']) or ''
        logger.debug('{Album} %s/new-album/%s', user_name, album_title)
        result = create_new_album(current_user.name, album_title)
        if result['success']:
            return redirect(url_for('user.index', user_name=current_user.name))
        else:
            flash('Can\'t create new album "%s"' % album_title)

    env = {
        'module': 'Create new album',
        'header': True,
        'errors': get_flashed_messages()
    }
    return render_template('album_new.html', **env)


# TODO: move this function to somewhere else?
def create_new_album(user_name, album_title):
    success = False
    # TODO: check for allowed characters
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            user = db.query_one(cur, 'SELECT id_user FROM app.user WHERE user_name=%(name)s;', {'name': user_name})
            album = db.query_one(
                cur,
                'SELECT id_album FROM app.album WHERE album_title = %(album)s and fk_user = %(user)s;',
                {'album': album_title, 'user': user.id_user})
            if not album.id_album:
                cur.execute(
                    'INSERT INTO app.album (album_title, fk_user) VALUES (%(title)s, %(user)s);',
                    {'title': album_title, 'user': user.id_user})
                success = True

    return {'success': success}



@album_module.route('/user/<user_name>/album/<album_title>/delete/', methods=['GET', 'POST'])
@login_required
def delete_album(user_name, album_title):
    logger.debug('{Album} %s/new-album', user_name)
    if user_name != current_user.name:
        return redirect(url_for('album.index', user_name=current_user.name))

    if request.method == 'POST':
        result = delete_one_album(user_name, album_title)
        if result['success']:
            if result['success']:
                flash('Successfully deleted album "%s"' % album_title)
                return redirect(url_for('user.index', user_name=current_user.name))
            else:
                flash('Can\'t delete album "%s"' % album_title)

    env = {
        'album_title': album_title,
    }
    return render_template('album_delete.html', **env)


def delete_one_album(user_name, album_title):
    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            # TODO: CASCADE
            user = db.query_one(cur, 'SELECT id_user FROM app.user WHERE user_name=%(name)s;', {'name': user_name})
            cur.execute(
                'DELETE FROM app.album WHERE fk_user=%(user)s AND album_title=%(album)s',
                {'user': user.id_user, 'album': album_title}
            )
            success=True

    return {'success': success}
