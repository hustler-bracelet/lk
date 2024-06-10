from __future__ import annotations

from datetime import datetime

from hustler_bracelet_lk.enums import TransactionType, TransactionStatus
from hustler_bracelet_lk.repos.bracelet_transaction import bracelet_transaction_repository
from hustler_bracelet_lk.database.models import BraceletTransaction, User


class TransactionManager:
    def __init__(self, user: User):
        self._user = user

    async def create_pending_transaction(
            self,
            transaction_type: TransactionType,
            amount: float,
            reason: str | None = None
    ) -> BraceletTransaction:
        new_transaction = BraceletTransaction(
            telegram_id=self._user.telegram_id,
            type=transaction_type,
            status=TransactionStatus.PENDING,
            amount=amount,
            reason=reason
        )
        await bracelet_transaction_repository.create(new_transaction)
        return new_transaction

    @staticmethod
    async def _process_transaction(transaction: BraceletTransaction, status: TransactionStatus) -> BraceletTransaction:
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

    async def get_all_transactions(self) -> list[BraceletTransaction]:
        all_transactions = await bracelet_transaction_repository.filter()
        return [
            transaction for transaction in all_transactions
            if transaction.telegram_id == self._user.telegram_id
        ]  # TODO: костыль!
