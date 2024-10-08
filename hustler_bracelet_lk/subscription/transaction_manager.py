from __future__ import annotations

from datetime import datetime

from hustler_bracelet_lk.enums import TransactionType, TransactionStatus
from hustler_bracelet_lk.repos.bracelet_transaction import get_bracelet_transaction_repository
from hustler_bracelet_lk.database.models import BraceletTransaction, User


class TransactionManager:
    def __init__(self, user: User, session):
        self._user = user
        self._session = session

    async def create_pending_transaction(
            self,
            transaction_type: TransactionType,
            amount: float,
            reason: str | None = None
    ) -> BraceletTransaction:
        bracelet_transaction_repository = get_bracelet_transaction_repository(self._session) 
        new_transaction = BraceletTransaction(
            telegram_id=await self._user.awaitable_attrs.telegram_id,
            type=transaction_type,
            status=TransactionStatus.PENDING,
            amount=amount,
            reason=reason
        )
        await bracelet_transaction_repository.create(new_transaction)
        return new_transaction

    async def _process_transaction(self, transaction: BraceletTransaction, status: TransactionStatus) -> BraceletTransaction:
        bracelet_transaction_repository = get_bracelet_transaction_repository(self._session)
        transaction.processed_at = datetime.now()
        transaction.status = status
        await bracelet_transaction_repository.update(transaction)
        return transaction

    async def approve_transaction(self, transaction: BraceletTransaction) -> TransactionManager:
        await self._process_transaction(transaction, status=TransactionStatus.SUCCESS)
        return self

    async def decline_transaction(self, transaction: BraceletTransaction) -> TransactionManager:
        await self._process_transaction(transaction, status=TransactionStatus.DECLINED)
        return self

    async def get_all_transactions(self, of_type: TransactionType) -> list[BraceletTransaction]:
        bracelet_transaction_repository = get_bracelet_transaction_repository(self._session) 
        return await bracelet_transaction_repository.filter_by(
            telegram_id=await self._user.awaitable_attrs.telegram_id,
            type=of_type
        )
