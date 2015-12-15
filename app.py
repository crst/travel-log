from importlib import import_module
import sys

from util import get_logger, config
logger = get_logger(__name__)

from flask import Flask
flask_app = Flask(__name__)


# Register modules
MODULES = [
    'user',
    'album',
    'edit',
    'share',
]

for module in MODULES:
    mod_name = 'modules.%s' % module
    blueprint_name = '%s_module' % module
    try:
        mod = import_module(mod_name)
        blueprint = getattr(mod, blueprint_name)
        flask_app.register_blueprint(blueprint)
        logger.debug('Loaded module %s', mod_name)
    except ImportError as err:
        logger.critical('No such module: %s', err)
        sys.exit(-1)
    except AttributeError as err:
        logger.critical('Module is missing the expected blueprint: %s', err)
        sys.exit(-1)


@flask_app.route('/')
def index():
    logger.debug('{Index}')
    return 'Index'


if __name__ == '__main__':
    logger.debug('Starting app')
    flask_app.run(debug=config['debug'])
