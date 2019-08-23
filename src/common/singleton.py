from __future__ import annotations


class SingletonMetaClass(type):
    __instances: dict = {}

    def __call__(cls: SingletonMetaClass, *args: list, **kwargs: dict) -> object:
        if cls not in cls.__instances:
            cls.__instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]
