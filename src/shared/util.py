import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import sys


configs = [
    'config.json',
    'config_local.json',
]

def load_config():
    result = {}

    for c in configs:
        if os.path.isfile(c):
            try:
                with open(c, 'r') as f:
                    cnf = json.load(f)
                    for k, v in cnf.items():
                        result[k] = v
            except Exception as e:
                print('Error reading config: %s' % c)
                print(e)
                sys.exit(-1)

    return result

config = load_config()


def get_logger(name):
    log_folder = config['log-folder']
    if not os.path.isdir(log_folder):
        os.makedirs(log_folder)

    logger = logging.getLogger(name)
    if not getattr(logger, 'has_handler', False):
        logger.setLevel(logging.getLevelName(config['log-level']))
        handler = RotatingFileHandler(os.path.join(log_folder, 'app.log'), maxBytes=1024 * 1024 * 50, backupCount=5)
        formatter = logging.Formatter(
            '[%(asctime)s] - {%(processName)s:%(threadName)s:%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.has_handler = True

    return logger


def log_request(request, current_user):
    # TODO: request logging should happen asynchronously

    log_folder = config['log-folder']
    if not os.path.isdir(log_folder):
        os.makedirs(log_folder)

    logger = logging.getLogger(__name__)
    if not getattr(logger, 'has_handler', False):
        logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler(os.path.join(log_folder, 'request.log'), when='midnight', interval=1, utc=True)
        formatter = logging.Formatter('"%(asctime)s";"%(message)s"')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.has_handler = True

    data = [
        hash_to_int(request.environ['REMOTE_ADDR']),
        str(int(current_user.is_anonymous)),
        hash_to_int(str(current_user.get_id())),
        request.method,
        str(int(request.is_secure)),
        str(int(request.is_xhr)),
        request.path,
        request.environ['QUERY_STRING'],
        str(request.user_agent.browser),
        str(request.user_agent.platform),
    ]
    logger.info('";"'.join(data))


def hash_to_int(msg, n=32):
    salt = config['SECRET_KEY']
    return str(int(hashlib.md5('%s%s' % (salt, msg)).hexdigest(), 16) % (2**n))
