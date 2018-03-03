import logging
import uuid
import flask
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

from utils.config import get_config


def generate_request_id(original_id=''):
    new_id = uuid.uuid4()

    if original_id:
        new_id = "{},{}".format(original_id, new_id)

    return new_id


# Returns the current request ID or a new one if there is none
# In order of preference:
#   * If we've already created a request ID and stored it in the flask.g context local, use that
#   * If a client has passed in the X-Request-Id header, create a new ID with that prepended
#   * Otherwise, generate a request ID and store it in flask.g.request_id
def request_id():
    if getattr(flask.g, 'request_id', None):
        return flask.g.request_id

    headers = flask.request.headers
    original_request_id = headers.get("X-Request-Id")
    new_uuid = generate_request_id(original_request_id)
    flask.g.request_id = new_uuid

    return new_uuid


LOGFORMAT = " [%(asctime)s] [%(name)s] [%(levelname)s] [%(request_id)s] - %(message)s"
COLOR_LOGFORMAT = "  %(log_color)s[%(asctime)s] [%(levelname)-5s] (%(request_id)s) [%(name)s:%(lineno)s]%(reset)s - %(log_color)s%(message)s%(reset)s"

file_formatter = logging.Formatter(LOGFORMAT)
colored_formatter = ColoredFormatter(COLOR_LOGFORMAT)


# Request filter
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id() if flask.has_request_context() else ''
        return True


# Handlers
class CustomConsoleHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        StreamHandler.__init__(self, *args, **kwargs)
        self.addFilter(RequestIdFilter())
        self.setFormatter(colored_formatter)


class CustomFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        RotatingFileHandler.__init__(self, *args, **kwargs)
        self.addFilter(RequestIdFilter())
        self.setFormatter(file_formatter)


logging.root.addHandler(CustomConsoleHandler())
logging.root.setLevel(logging.ERROR)
logging = logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.addHandler(CustomConsoleHandler())
    if (get_config()['environmet']['log']['file']['active'] is True):
        logger.addFilter(CustomFileHandler())
    logger.setLevel(logging.getLevelName(get_config()['environmet']['log']['level']))
    return logger
