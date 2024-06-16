from __future__ import annotations

from datetime import datetime, timedelta, tzinfo
from dateutil.relativedelta import relativedelta

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

        last_user_sub = await bracelet_subscription_repository.get_last_subscription(
            telegram_id=telegram_id
        )

        if last_user_sub:
            return last_user_sub

        now = datetime.now()
        now = pytz.timezone('Europe/Moscow').localize(now)

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
                will_end_on=datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=30)
            )
            await bracelet_subscription_repository.create(new_subscription)
            return new_subscription

    async def subscribe(self, bracelet_transaction: BraceletTransaction) -> BraceletSubscription:
        bracelet_subscription_repository = get_bracelet_subscription_repository(self._session)

        if await self.get_user_subscription():
            raise UserAlreadyAddedError

        if (await bracelet_transaction.awaitable_attrs.status) != TransactionStatus.SUCCESS:
            raise TransactionNotApprovedError

        new_subscription = BraceletSubscription(
            telegram_id=await self._user.awaitable_attrs.telegram_id,
            transaction_id=await bracelet_transaction.awaitable_attrs.id,
            will_end_on=datetime.now(pytz.timezone('Europe/Moscow')) + relativedelta(months=1)
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

        current_subscription.will_end_on = current_subscription.will_end_on + relativedelta(months=1)

        await bracelet_subscription_repository.update(current_subscription)

        return current_subscription
