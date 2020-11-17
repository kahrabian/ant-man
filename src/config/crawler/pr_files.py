from __future__ import annotations

from ..base import BaseConfig


class PRFilesConfig(BaseConfig):
    _path: str = f'{BaseConfig._path}/crawler/pr_files.ini'
