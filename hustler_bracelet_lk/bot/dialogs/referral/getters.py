from aiogram_dialog import DialogManager
from datetime import datetime

from hustler_bracelet_lk.referral.payout_calculator import PayoutCalculator
from hustler_bracelet_lk.referral.service import ReferralService
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager
from hustler_bracelet_lk.subscription.subscription_manager import SubscriptionManager
from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager


async def referral_dialog_getter(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.middleware_data['user']
    transaction_manager = TransactionManager(user)
    bracelet_channel_manager = BraceletChannelManager(user, dialog_manager.event.bot)
    referral_service = ReferralService(user, SubscriptionManager(user, bracelet_channel_manager))
    payout_calculator = PayoutCalculator(referral_service, transaction_manager)

    referred_users_amount = len(await referral_service.get_referred_users())
    referral_payout_rub = await payout_calculator.get_total_payout()

    my_id = dialog_manager.middleware_data['user'].telegram_id

    async def get_serialized_referred_users() -> list[dict]:
        # чучуть говнокод чучуть похуй...
        individual_payouts = await payout_calculator.get_individual_payouts()
        return [
            {
                'name': await payout[0].awaitable_attrs.telegram_name,
                'payout': payout[1]
            }
            for payout in individual_payouts
        ]

    return {
        'referred_users_amount': referred_users_amount,
        'referral_payout_rub': referral_payout_rub,
        'referral_link': f'https://t.me/hustler_bracelet_bot?start={my_id}',
        'referred_users': await get_serialized_referred_users()
    }
