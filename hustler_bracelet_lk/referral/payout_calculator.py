from hustler_bracelet_lk.referral.service import ReferralService
from collections import namedtuple

UserPayoutInfo = namedtuple('UserPayoutInfo', ['user', 'payout'])


class PayoutCalculator:
    def __init__(self, referral_service: ReferralService):
        self._referral_service = referral_service

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
        return sum([payout[1] for payout in payouts])
