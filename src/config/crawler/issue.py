from __future__ import annotations

from configparser import ConfigParser

from ..base import BaseConfig


class IssueConfig(BaseConfig):
    _path: str = f'{BaseConfig._path}/crawler/issue.ini'

    def __init__(self: IssueConfig) -> None:
        self.issue_configs: dict = {}

        if not self._initialized:
            self._initialize()

    def _initialize(self: IssueConfig) -> None:
        config: ConfigParser = self._load(self._path)

        for section in config.sections():
            if section != 'root':
                self.issue_configs[section] = dict(config.items(section))

        self._initialized = True
