from __future__ import annotations

import json
import logging
import re

from .base import BaseCrawler
from ..config.crawler.pr_files import PRFilesConfig
from ..common.decorator import handle_exception

logger: logging.Logger = logging.getLogger(__name__)


class PRFilesCrawler(BaseCrawler):
    _path: str = f'%s/files?page=1'
    _save_path: str = f'{BaseCrawler._save_path}/pr_files'
    _save_field: str = None
    _headers: dict = {'Accept': 'application/vnd.github.symmetra-preview+json'}
    _page_limit: str = '100'
    _config: PRFilesConfig = PRFilesConfig()

    @handle_exception
    def _crawl(self: PRFilesCrawler, pr_files_config: dict) -> None:
        with open(pr_files_config['path'], 'r') as f:
            pr_url: dict = json.loads(f.read())
        for i, (pr, url) in enumerate(pr_url.items()):
            self._retrieve(re.findall('/pr/(.*)', pr)[0], self._path % url)
            if i % 100 == 0:
                logger.error(f'{i} PRs crawled')
