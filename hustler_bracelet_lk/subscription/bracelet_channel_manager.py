from __future__ import annotations

import config
from aiogram import Bot

from hustler_bracelet_lk.database import User
from .errors import (
    UserNotSubscribedError,
    UserAlreadyAddedError
)


class BraceletChannelManager:
    def __init__(self, user: User, bot: Bot):
        self._user = user
        self._bot = bot

    async def add_user(self) -> BraceletChannelManager:
        ...

    async def remove_user(self) -> BraceletChannelManager:
        ...

    async def is_subscribed_to_channel(self) -> bool:  # noqa
        user = await self._bot.get_chat_member(
            chat_id=config.BRACELET_CHANNEL_ID,
            user_id=await self._user.awaitable_attrs.telegram_id
        )
        return user.status != "left"
