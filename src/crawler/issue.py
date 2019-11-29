from __future__ import annotations

import json
import logging

from .base import BaseCrawler
from ..config.crawler.issue import IssueConfig
from ..common.decorator import handle_exception

logger: logging.Logger = logging.getLogger(__name__)


class IssueCrawler(BaseCrawler):
    _path: str = f'{BaseCrawler._path}/repos/%s/issues'
    _save_path: str = f'{BaseCrawler._save_path}/issue'
    _save_field: str = None
    _headers: dict = {'Accept': 'application/vnd.github.symmetra-preview+json'}
    _page_limit: str = None
    _config: IssueConfig = IssueConfig()

    def _build_path(self: IssueCrawler, issue_config: dict, full_name: str) -> str:
        _filter: str = issue_config['filter']
        state: str = issue_config['state']
        sort: str = issue_config['sort']
        direction: str = issue_config['direction']
        return f'{self._path % (full_name,)}?filter={_filter}&state={state}&sort={sort}&direction={direction}&page=1'

    @handle_exception
    def _crawl(self: IssueCrawler, issue_config: dict) -> None:
        repo_path: str = issue_config['path']
        with open(repo_path, 'r') as f:
            repos: list = f.read().split('\n')
        total_issues: int = 0
        for repo_info in repos[:-1]:
            name: str = json.loads(repo_info)['full_name']
            path: str = self._build_path(issue_config, name)
            num_issues: int = self._retrieve(name, path)
            total_issues += num_issues
            logger.info(f'successfully crawled {num_issues} issues, total of {total_issues} issues so far')
