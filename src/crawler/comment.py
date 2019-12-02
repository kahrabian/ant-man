from __future__ import annotations

import glob
import json
import logging
import re

from .base import BaseCrawler
from ..config.crawler.comment import CommentConfig
from ..common.decorator import handle_exception

logger: logging.Logger = logging.getLogger(__name__)


class CommentCrawler(BaseCrawler):
    _save_path: str = f'{BaseCrawler._save_path}/comment'
    _save_field: str = None
    _headers: dict = {'Accept': 'application/vnd.github.v3.full+json'}
    _page_limit: str = None
    _config: CommentConfig = CommentConfig()

    _name_regex = re.compile(r'^.*/repos/(.*)/issues/(.*)/.*$')

    def _build_path(self: CommentCrawler, comments_url: str) -> str:
        return f'{comments_url}?&page=1'

    @handle_exception
    def _crawl(self: CommentCrawler, comment_config: dict) -> None:
        issue_path_pattern: str = comment_config['path_pattern']
        for issue_path in glob.glob(issue_path_pattern, recursive=True):
            with open(issue_path, 'r') as f:
                issues: list = f.read().split('\n')
            total_comments: int = 0
            for issue_info in issues[:-1]:
                path: str = self._build_path(json.loads(issue_info)['comments_url'])
                name: str = '/'.join(re.match(self._name_regex, path).groups())
                num_comments: int = self._retrieve(name, path)
                total_comments += num_comments
                if num_comments > 0:
                    logger.info(f'{num_comments} comments crawled, total: {total_comments}')
