from importlib import import_module
import sys

from flask import Flask
from flask.ext.login import LoginManager

import db
from util import get_logger, config
logger = get_logger(__name__)


flask_app = Flask(__name__)


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


if __name__ == '__main__':
    logger.debug('Starting app')
    flask_app.run(debug=config['debug'])
