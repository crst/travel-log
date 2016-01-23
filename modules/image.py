
from flask import Blueprint, send_from_directory

from util import config, get_logger
logger = get_logger(__name__)


image_module = Blueprint('image', __name__)


@image_module.route('/images/<path:filename>')
def images(filename):
    logger.debug('{Image} %s' % filename)
    return send_from_directory(config['storage-engine']['path'], filename)
