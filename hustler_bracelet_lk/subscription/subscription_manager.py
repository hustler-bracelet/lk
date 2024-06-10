from __future__ import annotations

from datetime import datetime, timedelta

from hustler_bracelet_lk.repos.bracelet_subscription import bracelet_subscription_repository
from hustler_bracelet_lk.database.models import BraceletSubscription, BraceletTransaction, User
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager

from .errors import (
    TransactionNotApprovedError,
    UserAlreadyAddedError,
    UserAlreadyRemovedError,
    UnmigratedSubscriptionError
)

from ..enums import TransactionStatus


class SubscriptionManager:
    def __init__(self, user: User, bracelet_channel_manager: BraceletChannelManager):
        self._user = user
        self._bracelet_channel_manager = bracelet_channel_manager

    async def get_user_subscription(self) -> BraceletSubscription | None:
        all_subscriptions = await bracelet_subscription_repository.filter()
        all_user_subscriptions = [
            sub for sub in all_subscriptions
            if sub.telegram_id == self._user.telegram_id
        ]

        now = datetime.now()
        for subscription in all_user_subscriptions:
            if subscription.started_on <= now <= subscription.will_end_on:
                return subscription

        if await self._bracelet_channel_manager.is_subscribed_to_channel():
            raise UnmigratedSubscriptionError

        return None

    async def subscribe(self, bracelet_transaction: BraceletTransaction) -> BraceletSubscription:
        if await self.get_user_subscription():
            raise UserAlreadyAddedError

        if bracelet_transaction.status != TransactionStatus.SUCCESS:
            raise TransactionNotApprovedError

        new_subscription = BraceletSubscription(
            telegram_id=self._user.telegram_id,
            transaction_id=bracelet_transaction.id,
            will_end_on=datetime.now() + timedelta(days=30)
        )
        await bracelet_subscription_repository.create(new_subscription)

        # TODO: add user to chat and channel

        return new_subscription

    async def unsubscribe(self) -> SubscriptionManager:
        current_subscription = await self.get_user_subscription()
        if not current_subscription:
            raise UserAlreadyRemovedError

        bracelet_subscription_repository.delete(current_subscription)

        # TODO: remove user from chat and channel

        return self

    async def extend_subscription(self) -> BraceletSubscription:
        current_subscription = await self.get_user_subscription()
        if not current_subscription:
            raise UserAlreadyRemovedError

        current_subscription.will_end_on += timedelta(days=30)
        bracelet_subscription_repository.update(current_subscription)

        return current_subscription
