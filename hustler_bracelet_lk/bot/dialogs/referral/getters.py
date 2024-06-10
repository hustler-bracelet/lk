from aiogram_dialog import DialogManager
from datetime import datetime

from hustler_bracelet_lk.referral.payout_calculator import PayoutCalculator
from hustler_bracelet_lk.referral.service import ReferralService


async def referral_dialog_getter(dialog_manager: DialogManager, **kwargs):
    referral_service = ReferralService(dialog_manager.middleware_data['user'])
    payout_calculator = PayoutCalculator(referral_service)

    referred_users_amount = len(await referral_service.get_referred_users())
    referral_payout_rub = await payout_calculator.get_total_payout()

    my_id = dialog_manager.middleware_data['user'].telegram_id

    async def get_serialized_referred_users() -> list[dict]:
        # чучуть говнокод чучуть похуй...
        individual_payouts = await payout_calculator.get_individual_payouts()
        return [
            {'name': payout[0], 'joined_on': datetime(2024, 6, 8), 'payout': payout[1]}
            for payout in individual_payouts
        ]

    return {
        'referred_users_amount': referred_users_amount,
        'referral_payout_rub': referral_payout_rub,
        'referral_link': f'https://t.me/hustler_bracelet_bot?start={my_id}',
        'referred_users': await get_serialized_referred_users()
    }
