from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from time import sleep
from urllib.parse import unquote

import requests

from .base import BaseCrawler
from ..common.decorator import handle_exception
from ..config.crawler.topic import TopicConfig

logger: logging.Logger = logging.getLogger(__name__)


class TopicCrawler(BaseCrawler):
    _path: str = f'{BaseCrawler._path}/repositories'
    _save_path: str = f'{BaseCrawler._save_path}/topic'
    _config: TopicConfig = TopicConfig()

    _req_delay: int = 6
    _link_regex: re.Pattern = re.compile(r'<(?P<url>[^;]+)>; rel="(?P<rel>[^,]+)"')
    _page_regex: re.Pattern = re.compile(r'(?<=&page=)(?P<page>\d+)$')
    _log_search_regex: re.Pattern = re.compile(r'(?<=\?)(?P<query_params>.+)$')
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

    def _save(self: TopicCrawler, name: str, repos: list) -> int:
        num_repos: int = len(repos)
        with open(f'{self._save_path}/{name}.json', 'a') as f:
            for repo in repos:
                data: str = json.dumps(repo)
                f.write(f'{data}\n')
        return num_repos

    def _search(self: TopicCrawler, name: str, path: str) -> int:
        sleep(self._req_delay)  # NOTE: To avoid rate limiting

        query_params: str = re.findall(self._log_search_regex, path)[0]
        logger.info(f'starting crawling process for {query_params}')

        response: requests.Response = requests.get(path)
        content: str = response.content.decode('utf-8')

        if not response.ok:
            raise Exception(f'something went wrong while crawling: {content}')

        logger.info(
            f'crawling process finished with status code {response.status_code}')

        page_num: str = re.findall(self._page_regex, path)[0]
        link: list = {x[1]: unquote(x[0]) for x in re.findall(self._link_regex, response.headers.get('link', ''))}
        if page_num == '1' and 'last' in link:
            page_count: str = re.findall(self._page_regex, link['last'])[0]
            if page_count == '34':
                return -1  # NOTE: Should limit the query to avoid result limiting

        json_content: dict = json.loads(content)
        num_repos: int = self._save(name, json_content['items'])
        num_repos += self._search(name, link['next']) if 'next' in link else 0
        return num_repos

    @handle_exception
    def _crawl(self: TopicCrawler, name: str, topic_config: dict) -> None:
        latest: float = datetime.utcnow().timestamp()
        offset: float = self._initial_offset
        total_repos: int = 0
        while latest > 0:
            path: str = self._build_path(topic_config, latest, offset)
            num_repos: int = self._search(name, path)
            if num_repos == -1:
                offset *= self._decrease_rate
                query_params: str = re.findall(self._log_search_regex, path)[0]
                logger.info(f'result limiting occured while crawling {query_params}')
                continue
            total_repos += num_repos
            offset *= self._increase_rate
            latest -= offset
            logger.info(f'successfully crawled {num_repos} repositories, total of {total_repos} repositories so far')

    def run(self: TopicCrawler) -> None:
        for name, topic_config in self._config.topic_configs.items():
            self._crawl(name, topic_config)
