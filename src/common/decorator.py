import logging

logger = logging.getLogger(__name__)


def handle_exception(fn: callable) -> callable:
    def wrapper(*args: list, **kwargs: dict) -> object:
        try:
            return fn(*args, **kwargs)
        except Exception as err:
            logger.exception(err)
            return None

    return wrapper
