from __future__ import annotations

from ..base import BaseConfig


class CommentConfig(BaseConfig):
    _path: str = f'{BaseConfig._path}/crawler/comment.ini'
