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
        logger.error(error)
        raise Exception(error)
    else:
        logger.debug("Connection successful")
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        return conn


@asyncio.coroutine
def listen(conn, *, channel_name):

    with conn.cursor() as curs:
        curs.execute("LISTEN {channel_name};".format(channel_name=channel_name))
        logger.info("LISTEN {channel_name};".format(channel_name=channel_name))

        # adapted from http://initd.org/psycopg/docs/advanced.html#asynchronous-notifications
        while True:
            if select.select([conn], [], [], 5) == ([], [], []):  # 5 second timeout
                pass
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    log_msg = "channel: {channel} received payload: {payload}".format(
                        channel=notify.channel,
                        payload=notify.payload,
                    )
                    logger.info(log_msg)
                    try:
                        place_message(channel_name=notify.channel, message=notify.payload)
                    except Exception as error:
                        logging.error(error)
            logger.info("{channel_name} yields".format(channel_name=channel_name))
            yield from asyncio.sleep(0)


def place_message(*, channel_name, message):

    amqp_dsn = 'amqp://{user}:{passwd}@{host}:{port}/{vhost}'.format(
        user=project_settings.RABBITMQ_USER,
        passwd=project_settings.RABBITMQ_PASSWORD,
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
        loop.run_forever()
    except Exception as error:
        logger.error(error)
    finally:
        loop.close()
        conn.close()
        logger.info("All done, closing up connections!")


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        logger.info("KeyboadInterrupt. Good Bye!")
        sys.exit()
    except Exception as error:
        logger.error(error)
        logger.error("Unknown Exception. Good Bye!")
        sys.exit()
