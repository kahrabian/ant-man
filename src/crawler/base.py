from __future__ import annotations

import json
import logging
import os
import re
from time import sleep
from urllib.parse import unquote

import requests

from ..config.base import BaseConfig

logger: logging.Logger = logging.getLogger(__name__)

class BaseCrawler(object):
    _path: str = 'https://api.github.com'
    _save_path: str = './data'
    _save_field: str = None
    _headers: dict = None
    _page_limit: str = None
    _config: BaseConfig = None

    _mdirs_regex: re.Pattern = re.compile(r'(.*)/.*$')
    _req_delay: int = 6
    _link_regex: re.Pattern = re.compile(r'<(?P<url>[^;]+)>; rel="(?P<rel>[^,]+)"')
    _page_regex: re.Pattern = re.compile(r'(?<=&page=)(?P<page>\d+)$')
    _log_retrieve_regex: re.Pattern = re.compile(r'(?<=\?)(?P<query_params>.+)$')

    def _save(self: BaseCrawler, name: str, contents: dict) -> int:
        mdirs: list = re.findall(self._mdirs_regex, name)
        if len(mdirs) > 0:
            os.makedirs(f'{self._save_path}/{mdirs[0]}', exist_ok=True)
        if self._save_field is not None:
            contents = contents[self._save_field]
        with open(f'{self._save_path}/{name}.json', 'a') as f:
            for content in contents:
                data: str = json.dumps(content)
                f.write(f'{data}\n')
        return len(contents)

    def _retrieve(self: BaseCrawler, name: str, path: str) -> int:
        sleep(self._req_delay)  # NOTE: To avoid rate limiting

        query_params: str = ''
        if re.search(self._log_retrieve_regex, path):
            query_params = re.findall(self._log_retrieve_regex, path)[0]
        logger.info(f'starting crawling process for {query_params}')

        response: requests.Response = requests.get(path, headers=self._headers)
        content: str = response.content.decode('utf-8')

        if not response.ok:
            raise Exception(f'something went wrong while crawling: {content}')

        logger.info(f'crawling process finished with status code {response.status_code}')

        page_num: str = re.findall(self._page_regex, path)[0]
        link: list = {x[1]: unquote(x[0]) for x in re.findall(self._link_regex, response.headers.get('link', ''))}
        if page_num == '1' and 'last' in link:
            page_count: str = re.findall(self._page_regex, link['last'])[0]
            if page_count == self._page_limit:
                return -1  # NOTE: Should limit the query to avoid result limiting

        json_content: dict = json.loads(content)
        num_contents: int = self._save(name, json_content)
        num_contents += self._retrieve(name, link['next']) if 'next' in link else 0
        return num_contents

    def run(self: BaseCrawler) -> None:
        for config in self._config.configs.values():
            self._crawl(config)
