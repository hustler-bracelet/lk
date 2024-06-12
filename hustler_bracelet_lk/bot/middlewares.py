from typing import Callable, Any, Awaitable

from aiogram import types, BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from sqlmodel.ext.asyncio.session import AsyncSession

from config import BRACELET_CHANNEL_ID
# from hustler_bracelet_lk.database.engine import DATABASE_ENGINE
from hustler_bracelet_lk.database.models import User
from hustler_bracelet_lk.database.engine import SessionMaker
from hustler_bracelet_lk.repos.user import get_user_repository


async def database_middleware(
        handler: Callable[[types.Update | types.ErrorEvent, dict[str, Any]], Awaitable[Any]],
        event: types.Update | types.ErrorEvent,
        data: dict[str, Any]
) -> Any:
    # чучуть говнокод чучуть поебать абсолютно...

    raw_event = event
    if isinstance(event, types.ErrorEvent):
        event, exception = event.update, event.exception
        event = event.message or event.callback_query
        if event is None:
            raise exception

    telegram_id = event.from_user.id

    async with SessionMaker() as session:
        user_rpository = get_user_repository(session)
        user = await user_rpository.get_by_pk(telegram_id)
        if not user:
            user = await user_rpository.create(
                User(
                    telegram_id=telegram_id,
                    telegram_name=event.from_user.first_name
                )
            )

        data['user'] = user
        data['session'] = session

        return await handler(raw_event, data)
