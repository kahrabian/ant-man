from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from time import sleep
from urllib.parse import unquote

import requests

from ..config.base import BaseConfig
from ..common.decorator import handle_exception

logger: logging.Logger = logging.getLogger(__name__)


class BaseCrawler(object):
    _path: str = 'https://api.github.com'
    _save_path: str = './data'
    _save_field: str = None
    _incomplete_dir: str = 'incomplete'
    _complete_dir: str = 'complete'
    _headers: dict = None
    _page_limit: str = None
    _config: BaseConfig = None

    _mdirs_regex: re.Pattern = re.compile(r'(.*)/.*$')
    _link_regex: re.Pattern = re.compile(r'<(?P<url>[^;]+)>; rel="(?P<rel>[^,]+)"')
    _page_regex: re.Pattern = re.compile(r'(?<=[&?]page=)(?P<page>\d+)$')
    _log_retrieve_regex: re.Pattern = re.compile(r'(?<=\?)(?P<query_params>.+)$')

    def _save(self: BaseCrawler, name: str, contents: dict) -> int:
        mdirs: list = re.findall(self._mdirs_regex, name)
        if len(mdirs) > 0:
            os.makedirs(f'{self._save_path}/{self._incomplete_dir}/{mdirs[0]}', exist_ok=True)
            os.makedirs(f'{self._save_path}/{self._complete_dir}/{mdirs[0]}', exist_ok=True)
        if self._save_field is not None:
            contents = contents[self._save_field]
        with open(f'{self._save_path}/{self._incomplete_dir}/{name}.json', 'a') as f:
            for content in contents:
                data: str = json.dumps(content)
                f.write(f'{data}\n')
        return len(contents)

    @handle_exception
    def _retrieve(self: BaseCrawler, name: str, path: str, root: bool = True) -> int:
        complete_path: str = f'{self._save_path}/{self._complete_dir}/{name}.json'
        if os.path.exists(complete_path):
            logger.info(f'skipping {complete_path}')
            return 0

        incomplete_path: str = f'{self._save_path}/{self._incomplete_dir}/{name}.json'
        if root and os.path.exists(incomplete_path):
            os.remove(incomplete_path)

        query_params: str = ''
        if re.search(self._log_retrieve_regex, path):
            query_params = re.findall(self._log_retrieve_regex, path)[0]
        logger.info(f'starting {query_params}')

        token: str = os.getenv('OAUTH_TOKEN', '')
        self._headers['Authorization'] = f'token {token}'
        response: requests.Response = requests.get(path, headers=self._headers)
        if response.headers.get('X-RateLimit-Remaining') == '0':
            sleep_time: int = int(response.headers['X-RateLimit-Reset']) - datetime.now().timestamp()
            logger.info(f'sleeping for {sleep_time}')
            sleep(sleep_time)
        content: str = response.content.decode('utf-8')

        if not response.ok:
            logger.error(f'something went wrong while crawling {path}: {content}')

        page_num: str = re.findall(self._page_regex, path)[0]
        link: list = {x[1]: unquote(x[0]) for x in re.findall(self._link_regex, response.headers.get('link', ''))}
        if page_num == '1' and 'last' in link:
            page_count: str = re.findall(self._page_regex, link['last'])[0]
            if page_count == self._page_limit:
                return -1  # NOTE: Should limit the query to avoid result limiting

        json_content: dict = json.loads(content)
        num_contents: int = self._save(name, json_content)

        if 'next' in link:
            num_contents += self._retrieve(name, link['next'], root=False)
        else:
            os.rename(f'{self._save_path}/{self._incomplete_dir}/{name}.json',
                      f'{self._save_path}/{self._complete_dir}/{name}.json')

        return num_contents

    def _crawl(self: TopicCrawler, topic_config: dict) -> None:
        raise NotImplementedError(f'this method should be implemented in class {self.__class__}')

    def run(self: BaseCrawler) -> None:
        for config in self._config.configs.values():
            self._crawl(config)
