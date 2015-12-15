import json
import os
import sys

import logging
from logging.handlers import RotatingFileHandler


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
    logger = logging.getLogger(name)
    handler = RotatingFileHandler(os.path.join('log', 'app.log'), maxBytes=1024 * 1024 * 50, backupCount=5)
    formatter = logging.Formatter(
        '[%(asctime)s] - {%(processName)s:%(threadName)s:%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.getLevelName(config['log_level']))
    return logger
