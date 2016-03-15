import hashlib
from importlib import import_module
import random
import string
import sys

from flask import Flask, abort, render_template, request, session
from flask.ext.login import LoginManager, current_user

import db
from util import get_logger, config, log_request
logger = get_logger(__name__)


flask_app = Flask(__name__)
flask_app.config['PREFERRED_URL_SCHEME'] = 'https'


def init_app(cnf):
    flask_app.secret_key = cnf['SECRET_KEY']
    init_login()


def init_login():
    login_manager = LoginManager()
    login_manager.init_app(flask_app)
    login_manager.session_protection = 'strong'
    login_manager.login_message = ''
    login_manager.login_view = 'index.login'
    login_manager.user_loader(db.load_user)


def load_modules(cnf):
    for module in cnf['modules']:
        mod_name = 'modules.%s' % module
        try:
            flask_app.register_blueprint(getattr(import_module(mod_name), '%s_module' % module))
            logger.debug('Loaded module %s', mod_name)
        except Exception as err:
            logger.critical('Can\'t load module: %s', err)
            sys.exit(-1)


init_app(config)
load_modules(config)


@flask_app.before_request
def csrf_protect():
    if request.method == 'POST':
        session_token = session.pop('_csrf_token', None)
        form_token = request.form.get('_csrf_token')
        if not form_token and '_csrf_token' in request.json:
            form_token = request.json['_csrf_token']

        if request.is_xhr:
            session['_csrf_token'] = session_token

        if not session_token or session_token != form_token:
            abort(400)


def generate_random_string():
    m = ''.join([random.choice(string.printable) for _ in range(16)])
    return hashlib.md5(m).hexdigest()

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = generate_random_string()
    return session['_csrf_token']

flask_app.jinja_env.globals['generate_csrf_token'] = generate_csrf_token


@flask_app.errorhandler(404)
def page_not_found(e):
    log_request(request, current_user)
    logger.debug('{Not found}')
    env = {'header': True}
    return render_template('404.html', **env), 404



if __name__ == '__main__':
    logger.debug('Starting app')

    context = None
    if 'ssl' in config and config['ssl']:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config['ssl-certificate'], config['ssl-key'])
    flask_app.run(debug=config['debug'], ssl_context=context)
