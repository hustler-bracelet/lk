from hustler_bracelet_lk.database import BraceletTransaction
from hustler_bracelet_lk.enums import TransactionType
from hustler_bracelet_lk.referral.service import ReferralService
from collections import namedtuple

from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager

UserPayoutInfo = namedtuple('UserPayoutInfo', ['user', 'payout'])


class PayoutCalculator:
    def __init__(
            self,
            referral_service: ReferralService,
            transaction_manager: TransactionManager
    ):
        self._referral_service = referral_service
        self._transaction_manager = transaction_manager

    async def get_all_payouts(self) -> list[BraceletTransaction]:
        return await self._transaction_manager.get_all_transactions(
            of_type=TransactionType.OUTCOME
        )

    async def get_individual_payouts(self) -> list[UserPayoutInfo]:
        result: list[UserPayoutInfo] = []
        referred_users = await self._referral_service.get_referred_users()
        for i, user in enumerate(referred_users, start=1):
            if i < 10:
                result.append(UserPayoutInfo(user, 100.0))
            elif i > 10:
                result.append(UserPayoutInfo(user, 200.0))

        return result

    async def get_total_payout(self) -> float:
        payouts = await self.get_individual_payouts()
        total_payout = sum([payout[1] for payout in payouts])

        all_payouts = await self.get_all_payouts()
        paid_out_sum = sum([await payout.awaitable_attrs.amount for payout in all_payouts])

        return total_payout - paid_out_sum
