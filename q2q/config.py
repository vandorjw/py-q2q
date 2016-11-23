import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTGRESQL_HOST = os.environ.get('POSTGRESQL_HOST', 'localhost')
POSTGRESQL_USER = os.environ.get('POSTGRESQL_USER', 'dev')
POSTGRESQL_PASSWORD = os.environ.get('POSTGRESQL_PASSWORD', 'dev')
POSTGRESQL_DATABASE = os.environ.get('POSTGRESQL_DATABASE', 'dev')
POSTGRESQL_PORT = os.environ.get('POSTGRESQL_DATABASE', '5432')
POSTGRESQL_CHANNELS = os.environ.get('POSTGRESQL_CHANNELS', 'channel1,channel2').split(',')

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'dev')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'dev')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', '5672')
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', 'dev')


LOG_DIR = os.environ.setdefault('LOG_DIR', os.path.join(PROJECT_ROOT, 'logs'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y/%m/%d %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'python.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'project': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
}