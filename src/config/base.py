from __future__ import annotations

import os
from configparser import ConfigParser

from ..common.singleton import SingletonMetaClass


class BaseConfig(object, metaclass=SingletonMetaClass):
    _initialized: bool = False
    _path: str = f'{os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}/resources/config'

    @staticmethod
    def _load(path: str) -> ConfigParser:
        config: ConfigParser = ConfigParser()
        config.read(path, 'utf-8')
        return config

    def _initialize(self: BaseConfig) -> None:
        assert NotImplementedError(f'This method should be implemented by the {self.__class__} class')
