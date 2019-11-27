from __future__ import annotations

from ..base import BaseConfig


class TopicConfig(BaseConfig):
    _path: str = f'{BaseConfig._path}/crawler/topic.ini'
