from __future__ import annotations

import json
import logging
import re
from datetime import datetime

from .base import BaseCrawler
from ..common.decorator import handle_exception
from ..config.crawler.topic import TopicConfig

logger: logging.Logger = logging.getLogger(__name__)


class TopicCrawler(BaseCrawler):
    _path: str = f'{BaseCrawler._path}/search/repositories'
    _save_path: str = f'{BaseCrawler._save_path}/topic'
    _save_field: str = 'items'
    _headers: dict = {'Accept': 'application/vnd.github.mercy-preview+json'}
    _page_limit: str = '34'
    _config: TopicConfig = TopicConfig()

    _time_format: str = '%Y-%m-%dT%H:%M:%S'
    _initial_offset: float = 60 * 60 * 24 * 365 * 1.0
    _increase_rate: float = 1.25
    _decrease_rate: float = 0.8

    def _build_path(self: TopicCrawler, topic_config: dict, latest: float, offset: float) -> str:
        q: str = topic_config['q']
        sort: str = topic_config['sort']
        order: str = topic_config['order']
        start: str = datetime.utcfromtimestamp(max(0, latest - offset)).strftime(self._time_format)
        end: str = datetime.utcfromtimestamp(latest).strftime(self._time_format)
        return f'{self._path}?q={q}+created:{start}..{end}&sort={sort}&order={order}&page=1'

    @handle_exception
    def _crawl(self: TopicCrawler, topic_config: dict) -> None:
        name: str = topic_config['name']
        latest: float = datetime.utcnow().timestamp()
        offset: float = self._initial_offset
        total_repos: int = 0
        while latest > 0:
            path: str = self._build_path(topic_config, latest, offset)
            num_repos: int = self._retrieve(name, path)
            if num_repos == -1:
                offset *= self._decrease_rate
                query_params: str = re.findall(self._log_retrieve_regex, path)[0]
                logger.info(f'result limiting {query_params}')
                continue
            total_repos += num_repos
            offset *= self._increase_rate
            latest -= offset
            if num_repos > 0:
                logger.info(f'{num_repos} repositories crawled, total: {total_repos}')
