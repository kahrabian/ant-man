from __future__ import annotations

from ..base import BaseConfig


class IssueConfig(BaseConfig):
    _path: str = f'{BaseConfig._path}/crawler/issue.ini'
