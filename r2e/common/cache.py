from collections import defaultdict
from typing import DefaultDict, Dict, Tuple
from r2e.models.context import Context
class DataCache(type):
    _caches: dict
    def __getitem__(cls, key):
        "<slug, identifier, type> -> <context>"
        return cls._caches[key]

    def __setitem__(cls, key, value):
        assert value is not None
        cls._caches[key] = value

class ContextCache(metaclass=DataCache):
    _caches: DefaultDict[Tuple[str, str, str], Context|None] = defaultdict(lambda: None)

