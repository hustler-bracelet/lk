from __future__ import annotations

import config
from hustler_bracelet_lk.database import User


class BraceletChannelManager:
    def __init__(self, user: User):
        self._user = user

    async def add_user(self) -> BraceletChannelManager:
        ...

    async def remove_user(self) -> BraceletChannelManager:
        ...

    async def is_subscribed_to_channel(self) -> bool:  # noqa
        user = await config.BOT.get_chat_member(
            chat_id=config.BRACELET_CHANNEL_ID,
            user_id=await self._user.awaitable_attrs.telegram_id
        )
        return user.status != "left"
