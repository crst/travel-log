
from flask import Blueprint, send_from_directory, request
from flask.ext.login import current_user

from shared.util import config, get_logger, log_request
logger = get_logger(__name__)


image_module = Blueprint('image', __name__)


@image_module.route('/images/<path:filename>')
def images(filename):
    log_request(request, current_user)
    logger.debug('{View|Image} images(%s)', filename)

    return send_from_directory(config['storage-engine']['path'], filename)
