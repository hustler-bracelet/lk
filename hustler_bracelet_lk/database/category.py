# -*- coding: utf-8 -*-

from sqlalchemy import Column, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import SQLModel, Field

from hustler_bracelet.enums import FinanceTransactionType


class Category(SQLModel, AsyncAttrs, table=True):
    id: int | None = Field(primary_key=True)
    telegram_id: int = Field(sa_column=Column(BigInteger()))
    name: str
    type: str
