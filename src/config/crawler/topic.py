from __future__ import annotations

from configparser import ConfigParser

from ..base import BaseConfig


class TopicConfig(BaseConfig):
    _path: str = f'{BaseConfig._path}/crawler/topic.ini'

    def __init__(self: TopicConfig) -> None:
        self.topics: dict = {}

        if not self._initialized:
            self._initialize()

    def _initialize(self: TopicConfig):
        config: ConfigParser = self._load(self._path)

        self.topics = {section: dict(config.items(section)) for section in config.sections() if section != 'root'}

        self._initialized = True
