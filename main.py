import logging
import sys
from logging import Formatter, RootLogger, StreamHandler
from logging.handlers import RotatingFileHandler


def config_logging(path: str, log_level: str = 'INFO') -> None:
    logger: RootLogger = logging.getLogger()
    logger.setLevel(log_level)

    formatter = Formatter('[%(levelname)s] %(asctime)s - %(name)s: %(message)s')

    stream_handler: StreamHandler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler: RotatingFileHandler = RotatingFileHandler(path, maxBytes=10485760, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def run() -> int:
    from src.crawler.comment import CommentCrawler
    CommentCrawler().run()
    return 0


def main() -> int:
    config_logging('./log/crawler.log')
    return run()


if __name__ == '__main__':
    exit(main())
