
from abc import ABC, abstractmethod
from typing import Any


class AbstractRepo(ABC):
    @abstractmethod
    async def get_by_pk(self, *args, **kwargs) -> Any:
        ...

    @abstractmethod
    async def filter(self, *args, **kwargs) -> Any:
        ...

    @abstractmethod
    async def create(self, *args, **kwargs) -> Any:
        ...

    @abstractmethod
    async def update(self, *args, **kwargs) -> Any:
        ...

    @abstractmethod
    async def delete(self, *args, **kwargs) -> Any:
        ...
