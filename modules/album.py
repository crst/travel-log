
from flask import Blueprint, escape, flash, get_flashed_messages, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_required

from util import config
import db
from util import get_logger
logger = get_logger(__name__)


album_module = Blueprint('album', __name__)


@album_module.route('/user/<username>/album/view/<title>/')
def index(username, title):
    logger.debug('{Album} %s/album/%s', username, title)
    env = {
        'module': 'Album',
        'title': title
    }
    return render_template('album.html', **env)


@album_module.route('/user/<username>/album/new', methods=['GET', 'POST'])
@login_required
def new_album(username):
    logger.debug('{Album} %s/new-album', username)
    if username != current_user.name:
        return redirect(url_for('album.new_album', username=current_user.name))

    if request.method == 'POST':
        album_name = 'album_name' in request.form and escape(request.form['album_name']) or ''
        logger.debug('{Album} %s/new-album/%s', username, album_name)
        result = create_new_album(current_user.name, album_name)
        if result['success']:
            return redirect(url_for('user.index', username=current_user.name))
        else:
            flash('Can\'t create new album "%s"' % album_name)

    env = {
        'module': 'Create new album',
        'header': True,
        'errors': get_flashed_messages()
    }
    return render_template('album_new.html', **env)


# TODO: move this function to somewhere else?
def create_new_album(user_name, album_name):
    success = False
    # TODO: check for allowed characters
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            user = db.query_one(cur, 'SELECT id_user FROM app.user WHERE user_name=%(name)s;', {'name': user_name})
            album = db.query_one(
                cur,
                'SELECT id_album FROM app.album WHERE album_title = %(album)s and fk_user = %(user)s;',
                {'album': album_name, 'user': user.id_user})
            if not album.id_album:
                cur.execute(
                    'INSERT INTO app.album (album_title, fk_user) VALUES (%(title)s, %(user)s);',
                    {'title': album_name, 'user': user.id_user})
                success = True

    return {'success': success}


@album_module.route('/user/<username>/album/<title>/delete/', methods=['GET', 'POST'])
@login_required
def delete_album(username, album):
    # TODO: Ask again, only actually delete if POST, also remove all items
    pass
