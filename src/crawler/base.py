from __future__ import annotations

from ..config.base import BaseConfig


class BaseCrawler(object):
    _path: str = 'https://api.github.com/search'
    _save_path: str = './data'
    _config: BaseConfig = None

    def run(self: BaseCrawler) -> None:
        raise NotImplementedError(f'This method should be implemented by the {self.__class__} class')
