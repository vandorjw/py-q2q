# -*- coding: utf-8 -*-
import asyncio
import logging
from logging.config import dictConfig
import select
import sys
from kombu import Connection
import psycopg2
import psycopg2.extensions
from q2q import config as project_settings

dictConfig(project_settings.LOGGING)
logger = logging.getLogger('project')


def get_db_connection():
    try:
        conn = psycopg2.connect(database=project_settings.POSTGRESQL_DATABASE,
                                password=project_settings.POSTGRESQL_PASSWORD,
                                user=project_settings.POSTGRESQL_USER,
                                port=project_settings.POSTGRESQL_PORT,
                                host=project_settings.POSTGRESQL_HOST)
    except Exception as error:
        logger.debug(error)
        logging.error(error)
        raise Exception(error)
    else:
        logger.debug("Connection successful")
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        return conn


@asyncio.coroutine
def listen(conn, *, channel_name):
    logger.debug("listening on channel: {channel_name};".format(channel_name=channel_name))

    curs = conn.cursor()
    curs.execute("LISTEN {channel_name};".format(channel_name=channel_name))
    logger.debug("LISTEN {channel_name};".format(channel_name=channel_name))

    # adapted from http://initd.org/psycopg/docs/advanced.html#asynchronous-notifications
    while True:
        if select.select([conn], [], [], 5) == ([], [], []):  # 5 second timeout
            pass
        else:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                logger.debug(notify)
                try:
                    place_message(channel_name=channel_name, message=notify.payload)
                except Exception as error:
                    logging.error(error)
        logger.debug("About to yield control of the thread for {channel_name};".format(channel_name=channel_name))
        yield from asyncio.sleep(0)


def place_message(*, channel_name, message):

    amqp_dsn = 'amqp://{user}:{passwd}@{host}:{port}/{vhost}'.format(
        user=project_settings.RABBITMQ_USER,
        passwd=project_settings.RABBITMQ_PASSWD,
        host=project_settings.RABBITMQ_HOST,
        port=project_settings.RABBITMQ_PORT,
        vhost=project_settings.RABBITMQ_VHOST,
    )

    with Connection(amqp_dsn) as conn:
        simple_queue = conn.SimpleQueue(channel_name)
        simple_queue.put(message)
        logger.info('Sent: %s' % message)
        simple_queue.close()


def run():
    conn = get_db_connection()

    loop = asyncio.get_event_loop()

    tasks = [
        asyncio.ensure_future(listen(conn, channel_name=channel)) for channel in project_settings.POSTGRESQL_CHANNELS
    ]

    try:
        logger.debug("Asking to loop forever")
        loop.run_forever()
        logger.debug("We will serve, forever")
    except Exception as error:
        logger.error(error)
    finally:
        logger.debug("All done!")
        loop.close()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        logging.info("KeyboadInterrupt. Good Bye!")
        sys.exit()
    except Exception as error:
        logging.error(error)
        logging.error("Unknown Exception. Good Bye!")
        sys.exit()
