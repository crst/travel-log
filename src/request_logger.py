import logging
from logging.handlers import TimedRotatingFileHandler
import os
from shared.util import config
import time

import pika


def get_logger(name):
    log_folder = config['log-folder']
    if not os.path.isdir(log_folder):
        os.makedirs(log_folder)

    logger = logging.getLogger(name)
    if not getattr(logger, 'has_handler', False):
        logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler(os.path.join(log_folder, 'request.log'), when='midnight', interval=1, utc=True)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.has_handler = True

    return logger


def run_logger():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['request-logger-host'], port=5673))
    channel = connection.channel()
    channel.exchange_declare(
        exchange='request_logs',
        exchange_type='fanout',
        durable=True,
        auto_delete=False
    )
    queue = channel.queue_declare(queue='request_logs', durable=True)
    queue_name = queue.method.queue
    channel.queue_bind(exchange='request_logs', queue=queue_name)

    logger = get_logger(__name__)
    def callback(ch, method, properties, body):
        logger.info(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue_name, callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    while True:
        try:
            run_logger()
        except Exception as err:
            print(f'Rabbitmq connection failed: {err}')
            time.sleep(30)
            print('Trying to run again!')
