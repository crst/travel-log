from flask import Blueprint, abort, escape, flash, get_flashed_messages, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_required

from common import check_auth, load_items
import db
from util import config, get_logger
logger = get_logger(__name__)


album_module = Blueprint('album', __name__)



@album_module.route('/user/<user_name>/album/view/<album_title>/')
def index(user_name, album_title):
    logger.debug('{Album} %s/album/%s', user_name, album_title)

    is_authorized = check_auth(current_user, user_name, album_title)
    if not is_authorized:
        return abort(404)

    env = {
        'module': 'Album',
        'header': False,
        'user': user_name,
        'album_title': album_title,
    }
    return render_template('album.html', **env)


@album_module.route('/user/<user_name>/album/view/<album_title>/get_items/')
def get_items(user_name, album_title):
    return load_items(current_user, user_name, album_title)


@album_module.route('/user/<user_name>/album/new', methods=['GET', 'POST'])
@login_required
def new_album(user_name):
    logger.debug('{Album} %s/new-album', user_name)
    if user_name != current_user.name:
        return redirect(url_for('album.new_album', user_name=current_user.name))

    if request.method == 'POST':
        album_title = 'album_title' in request.form and escape(request.form['album_title']) or 'No title'
        album_desc = 'album_desc' in request.form and escape(request.form['album_desc']) or 'No description'
        logger.debug('{Album} %s/new-album/%s', user_name, album_title)
        result = create_new_album(current_user.id_user, album_title, album_desc)
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


def create_new_album(id_user, album_title, album_desc):
    success = False
    # TODO: check for allowed characters
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            album = db.query_one(
                cur,
                'SELECT id_album FROM travel_log.album WHERE album_title = %(album)s and fk_user = %(user)s AND NOT is_deleted;',
                {'album': album_title, 'user': id_user})
            if not album.id_album:
                cur.execute(
                    'INSERT INTO travel_log.album (album_title, album_desc, fk_user) VALUES (%(title)s, %(desc)s, %(user)s);',
                    {'title': album_title, 'desc': album_desc, 'user': id_user})

                cur.execute('''
INSERT INTO travel_log.share (fk_album, fk_share_type, fk_user)
  SELECT
    id_album,
    id_share_type,
     %(user)s
  FROM travel_log.album a
  CROSS JOIN travel_log.share_type st
  WHERE a.fk_user = %(user)s
    AND a.album_title = %(title)s
    AND st.share_type_name = \'Private\'
                ''',
                {'title': album_title, 'user': id_user})
                success = True

    return {'success': success}



@album_module.route('/user/<user_name>/album/<album_title>/delete/', methods=['GET', 'POST'])
@login_required
def delete_album(user_name, album_title):
    logger.debug('{Album} %s/new-album', user_name)
    if user_name != current_user.name:
        return redirect(url_for('album.index', user_name=current_user.name))

    if request.method == 'POST':
        result = delete_one_album(current_user.id_user, album_title)
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


def delete_one_album(id_user, album_title):
    success = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            # TODO: only flag album as deleted here, some worker queue
            # should actually delete them (and cascade to items).
            cur.execute(
                'UPDATE travel_log.album SET is_deleted = TRUE WHERE fk_user=%(user)s AND album_title=%(album)s',
                {'user': id_user, 'album': album_title}
            )
            success = True

    return {'success': success}
