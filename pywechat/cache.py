import logging
import time
from typing import Optional, Tuple


logger = logging.getLogger(__name__)


class BaseCache:
    def get(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        raise NotImplementedError

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        raise NotImplementedError

    async def aget(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        raise NotImplementedError

    async def aset(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        raise NotImplementedError


class MemoryCache(BaseCache):
    def __init__(self):
        self._cache: dict[str, str] = {}
        self._expiry: dict[str, int] = {}

    def get(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        if key in self._expiry and self._expiry[key] < time.time():
            del self._cache[key]
            del self._expiry[key]
            return None, None
        return self._cache.get(key), self._expiry.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._cache[key] = value
        if ex is not None:
            self._expiry[key] = time.time() + ex
        return True

    async def aget(self, key: str) -> Tuple[Optional[str], Optional[int]]:
        return self.get(key)

    async def aset(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        return self.set(key, value, ex)
