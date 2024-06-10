from typing import Callable, Any, Awaitable

from aiogram import types, BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from sqlmodel.ext.asyncio.session import AsyncSession

from config import BRACELET_CHANNEL_ID
from hustler_bracelet_lk.database.engine import DATABASE_ENGINE
from hustler_bracelet_lk.database.models import User
from hustler_bracelet_lk.repos.user import user_repository


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
    user_cache: dict[int, User] = {}  # чтобы не обращаться к бд при каждом запросе
    did_create_user = False

    if telegram_id in user_cache.keys():
        user = user_cache[telegram_id]

    else:
        user = await user_repository.get_by_pk(telegram_id)
        if not user:
            try:
                referred_by = data['referred_by']
            except KeyError:
                referred_by = None

            user = await user_repository.create(
                User(
                    telegram_id=telegram_id,
                    telegram_name=event.from_user.first_name,
                    referred_by=referred_by
                )
            )
            did_create_user = True

        user_cache[telegram_id] = user

    data['user'] = user
    data['did_create_user'] = did_create_user

    return await handler(raw_event, data)
