from __future__ import annotations

import json
import logging
import re
from time import sleep
from urllib.parse import unquote

import requests
from requests import Response

from .base import BaseCrawler
from ..common.decorator import handle_exception
from ..config.crawler.topic import TopicConfig

logger = logging.getLogger(__name__)


class TopicCrawler(BaseCrawler):
    _path: str = f'{BaseCrawler._path}/repositories'
    _save_path: str = f'{BaseCrawler._save_path}/topic'
    _config: TopicConfig = TopicConfig()

    _req_delay: int = 6
    _link_regex: re.Pattern = re.compile(r'<(?P<url>[^;]*)>; rel="(?P<rel>[^,]*)"')
    _log_regex: re.Pattern = re.compile(r'(?<=&page=)(?P<page>\d+)$')

    def _build_path(self: TopicCrawler, topic_config: dict) -> str:
        q: str = topic_config['q']
        sort: str = topic_config['sort']
        order: str = topic_config['order']
        return f'{self._path}?q={q}&sort={sort}&order={order}&page=1'

    def _search(self: TopicCrawler, path: str) -> list:
        logger.info(f'starting crawling process: {path}')
        response: Response = requests.get(path)
        logger.info(f'crawling process finished with status code {response.status_code}')
        content: str = response.content.decode('utf-8')
        json_content: dict = json.loads(content)

        if not response.ok:
            raise Exception(f'something went wrong while crawling: {content}')

        link: list = {x[1]: unquote(x[0]) for x in re.findall(self._link_regex, response.headers['Link'])}
        if 'last' in link:
            logger.info('starting delay ...')
            sleep(self._req_delay)
            return self._search(link['next']) + json_content['items']        
        return json_content['items']

    def _save(self: TopicCrawler, name: str, repos: list) -> None:
        data: str = json.dumps(repos)
        with open(f'{self._save_path}/{name}.json', 'w') as f:
            f.write(data)

    @handle_exception
    def _crawl(self: TopicCrawler, name: str, topic_config: dict) -> None:
        path: str = self._build_path(topic_config)
        repos: list = self._search(path)
        self._save(name, repos)

    def run(self: TopicCrawler) -> None:
        for name, topic_config in self._config.topic_configs.items():
            self._crawl(name, topic_config)
