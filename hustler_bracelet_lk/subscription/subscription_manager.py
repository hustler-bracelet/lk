from __future__ import annotations

from datetime import datetime, timedelta, tzinfo

import pytz

from hustler_bracelet_lk.repos.bracelet_subscription import get_bracelet_subscription_repository
from hustler_bracelet_lk.repos.bracelet_transaction import get_bracelet_transaction_repository
from hustler_bracelet_lk.database.models import BraceletSubscription, BraceletTransaction, User
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager

from .errors import (
    TransactionNotApprovedError,
    UserAlreadyAddedError,
    UserAlreadyRemovedError
)

from ..enums import TransactionStatus, TransactionType


class SubscriptionManager:
    def __init__(self, user: User, bracelet_channel_manager: BraceletChannelManager, session):
        self._user = user
        self._bracelet_channel_manager = bracelet_channel_manager
        self._session = session

    async def get_user_subscription(
            self
    ) -> BraceletSubscription | None:
        telegram_id = await self._user.awaitable_attrs.telegram_id
        telegram_name = await self._user.awaitable_attrs.telegram_name

        bracelet_subscription_repository = get_bracelet_subscription_repository(self._session)
        bracelet_transaction_repository = get_bracelet_transaction_repository(self._session)

        all_user_subscriptions = await bracelet_subscription_repository.filter_by(
            telegram_id=telegram_id
        )

        now = datetime.now()
        now = pytz.timezone('Europe/Moscow').localize(now)
        for subscription in all_user_subscriptions:
            started_on = await subscription.awaitable_attrs.started_on
            will_end_on = await subscription.awaitable_attrs.will_end_on
            if started_on <= now <= will_end_on:
                return subscription

        if await self._bracelet_channel_manager.is_subscribed_to_channel():
            new_transaction = BraceletTransaction(
                telegram_id=telegram_id,
                type=TransactionType.INCOME,
                status=TransactionStatus.SUCCESS,
                amount=1000.0,
                reason=f'Миграция юзера {telegram_name} ({telegram_id}) ({now})',
                processed_at=now
            )
            await bracelet_transaction_repository.create(new_transaction)

            new_subscription = BraceletSubscription(
                telegram_id=telegram_id,
                transaction_id=await new_transaction.awaitable_attrs.id,
                will_end_on=datetime.now() + timedelta(days=30)
            )
            await bracelet_subscription_repository.create(new_subscription)
            return new_subscription

        return None

    async def subscribe(self, bracelet_transaction: BraceletTransaction) -> BraceletSubscription:
        bracelet_subscription_repository = get_bracelet_subscription_repository(self._session)

        if await self.get_user_subscription():
            raise UserAlreadyAddedError

        if (await bracelet_transaction.awaitable_attrs.status) != TransactionStatus.SUCCESS:
            raise TransactionNotApprovedError

        new_subscription = BraceletSubscription(
            telegram_id=await self._user.awaitable_attrs.telegram_id,
            transaction_id=await bracelet_transaction.awaitable_attrs.id,
            will_end_on=datetime.now() + timedelta(days=30)
        )
        await bracelet_subscription_repository.create(new_subscription)

        return new_subscription

    async def unsubscribe(self) -> SubscriptionManager:
        bracelet_subscription_repository = get_bracelet_subscription_repository(self._session)
        current_subscription = await self.get_user_subscription()
        if not current_subscription:
            raise UserAlreadyRemovedError

        await bracelet_subscription_repository.delete(current_subscription)

        return self

    async def extend_subscription(self) -> BraceletSubscription:
        bracelet_subscription_repository = get_bracelet_subscription_repository(self._session)

        current_subscription = await self.get_user_subscription()
        if not current_subscription:
            raise UserAlreadyRemovedError

        started_on = await current_subscription.awaitable_attrs.started_on
        current_subscription.will_end_on = started_on + timedelta(days=60)
        # NOTE: может не работать как надо в некоторых сценариях. надо потестить

        await bracelet_subscription_repository.update(current_subscription)

        return current_subscription
