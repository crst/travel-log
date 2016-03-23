import datetime
import hashlib
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

import pika

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
        handler = TimedRotatingFileHandler(os.path.join(log_folder, 'app.log'), when='midnight', interval=1, utc=True)
        formatter = logging.Formatter(
            '[%(asctime)s] - {%(processName)s:%(threadName)s:%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.has_handler = True

    return logger


def log_request(request, current_user):
    data = '";"'.join([
        datetime.datetime.utcnow().isoformat(' '),
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
    ])
    data = '"%s"' % data

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=config['request-logger-host']
        ))
        channel = connection.channel()
        channel.exchange_declare(
            exchange='request_logs',
            type='fanout',
            durable=True,
            auto_delete=False
        )
        channel.basic_publish(
            exchange='request_logs',
            routing_key='request_logs',
            body=data,
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        connection.close()
    except Exception as e:
        logger = get_logger(__name__)
        logger.error('Can\'t log request: %s', e)


def hash_to_int(msg, n=32):
    salt = config['SECRET_KEY']
    return str(int(hashlib.md5('%s%s' % (salt, msg)).hexdigest(), 16) % (2**n))
