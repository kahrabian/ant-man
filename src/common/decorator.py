import logging

logger = logging.getLogger(__name__)


def handle_exception(fn: callable) -> callable:
    def wrapper(*args: list, **kwargs: dict) -> None:
        try:
            fn(*args, **kwargs)
        except Exception as err:
            logger.exception(err)

    return wrapper
