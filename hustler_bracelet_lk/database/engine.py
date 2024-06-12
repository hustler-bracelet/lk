# -*- coding: utf-8 -*-

import config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
from sqlmodel import create_engine

# DATABASE_ENGINE = AsyncEngine(
#     create_engine(
#         url=URL(
#             drivername='postgresql+asyncpg',
#             username=config.DB_USER,
#             password=config.DB_PASS,
#             host=config.DB_HOST,
#             port=config.DB_PORT,
#             database=config.DB_NAME,
#             query={}
#         )
#     )
# )
postgres_uri = f'postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'

engine = create_async_engine(postgres_uri, pool_pre_ping=True)
SessionMaker = sessionmaker(engine, autoflush=False, class_=AsyncSession, expire_on_commit=False)


async def create_all_tables() -> None:
    async with DATABASE_ENGINE.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        # return await conn.run_sync(SQLModel.metadata.create_all)
        pass
