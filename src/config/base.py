from __future__ import annotations

import os
from configparser import ConfigParser

from ..common.singleton import SingletonMetaClass


class BaseConfig(object, metaclass=SingletonMetaClass):
    _initialized: bool = False
    _path: str = f'{os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}/resources/config'

    def __init__(self: BaseConfig) -> None:
        self.configs: dict = {}

        if not self._initialized:
            self._initialize()

    @staticmethod
    def _load(path: str) -> ConfigParser:
        config: ConfigParser = ConfigParser()
        config.read(path, 'utf-8')
        return config

    def _initialize(self: BaseConfig) -> None:
        config: ConfigParser = self._load(self._path)

        for section in config.sections():
            if section != 'root':
                self.configs[section] = dict(config.items(section))

        self._initialized = True
