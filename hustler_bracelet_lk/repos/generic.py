
from typing import TypeVar, Generic, Type, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hustler_bracelet_lk.database.models import BaseModel


M = TypeVar('M', bound=BaseModel)


GREATER_THAN = 'gt'
LESSER_THAN = 'lt'
GREATER_THAN_OR_EQUAL = 'gte'
LESSER_THAN_OR_EQUAL = 'lte'

_IN = 'in'


class QueryActionNotAllowedError(Exception):
    pass


class SimpleQueryParser:
    ALLOWED_COMPARISONS = [
        GREATER_THAN,
        LESSER_THAN,
        GREATER_THAN_OR_EQUAL,
        LESSER_THAN_OR_EQUAL,
        _IN,
    ]

    def __init__(self, delimiter: str | None = None) -> None:
        """
        Simple query parser for SQLAlchemy queries

        :param delimiter: delimiter for separating model fields, defaults to '__'
        """

        self._delimiter = delimiter or '__'

    def _extract_action(self, query: str) -> str:
        """
        Extract action from query string

        :param query: query string
        :return: action
        """
        return query.split(self._delimiter)[-1]

    def parse(self, query: str) -> str:
        """
        Parse query string to list of tuples (field, comparison, value)

        :param query: query string
        :return: list of tuples
        """
        query = query.strip()

        action = self._extract_action(query)

        if action not in self.ALLOWED_COMPARISONS:
            raise QueryActionNotAllowedError(f'Unsupported action: {action}')

        return action


class Repository(Generic[M]):
    def __init__(self, model: Type[M], session: AsyncSession) -> None:
        self._model = model
        self._session = session
        self._parser = SimpleQueryParser(delimiter='__')

    async def get_by_pk(self, pk: int, options: list | None = None) -> M:
        """Get record by primary key"""
        return await self._session.get(self._model, pk, options=options)

    async def filter(self, **kwargs) -> list[M]:
        """
        Filter models by kwargs

        :param kwargs: model fields and their values
        :return: list of records
        """
        query = select(self._model)

        for field, value in kwargs.items():
            action = self._parser.parse(field)

            if action == GREATER_THAN:
                query = query.where(getattr(self._model, field) > value)
            elif action == LESSER_THAN:
                query = query.where(getattr(self._model, field) < value)
            elif action == GREATER_THAN_OR_EQUAL:
                query = query.where(getattr(self._model, field) >= value)
            elif action == LESSER_THAN_OR_EQUAL:
                query = query.where(getattr(self._model, field) <= value)
            elif action == _IN:
                query = query.where(getattr(self._model, field).in_(value))
            else:
                raise QueryActionNotAllowedError(f'Unsupported action: {action}')

        return (await self._session.execute(query)).scalars().all()

    async def filter_by(self, options: list | None = None, **filters) -> Sequence[M] | None:
        query = (
            select(self._model)
            .filter_by(**filters)
            # .order_by(self._model.id.asc())
        )

        if options:
            query = query.options(*options)

        return (await self._session.execute(query)).scalars().all()

    async def create(self, model: M, with_commit: bool = True) -> M:
        """Create model in database"""
        self._session.add(model)
        await self._session.flush()

        if with_commit:
            await self._session.commit()

        return model

    async def bulk_create(self, models: list[M], with_commit: bool = True) -> list[M]:
        """Create models in database"""
        self._session.add_all(models)
        await self._session.flush()

        if with_commit:
            await self._session.commit()

        return models

    async def update(self, model: M, with_commit: bool = True) -> M:
        """Update model in database"""
        await self._session.merge(model)
        await self._session.flush()

        if with_commit:
            await self._session.commit()

        return model

    async def delete(self, model: M, with_commit: bool = True) -> M:
        """Delete model from database"""
        await self._session.delete(model)
        await self._session.flush()

        if with_commit:
            await self._session.commit()

        return model

    async def commit(self):
        await self._session.commit()
