from importlib import import_module
import sys

from flask import Flask, render_template
from flask.ext.login import LoginManager

import db
from util import get_logger, config
logger = get_logger(__name__)


flask_app = Flask(__name__)
flask_app.config['PREFERRED_URL_SCHEME'] = 'https'


def init_app(cnf):
    flask_app.secret_key = cnf['SECRET_KEY']
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


@flask_app.errorhandler(404)
def page_not_found(e):
    logger.debug('{Not found}')
    env = {'header': True}
    return render_template('404.html', **env), 404


if __name__ == '__main__':
    logger.debug('Starting app')

    context = None
    if config['ssl']:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config['ssl-certificate'], config['ssl-key'])
    flask_app.run(debug=config['debug'], ssl_context=context)
