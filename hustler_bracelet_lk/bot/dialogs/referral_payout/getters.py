from aiogram_dialog import DialogManager
from datetime import datetime

from hustler_bracelet_lk.database import User
from hustler_bracelet_lk.referral.payout_calculator import PayoutCalculator
from hustler_bracelet_lk.referral.service import ReferralService
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager
from hustler_bracelet_lk.subscription.subscription_manager import SubscriptionManager
from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager


async def referral_payout_dialog_getter(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.middleware_data['user']
    transaction_manager = TransactionManager(user)
    bracelet_channel_manager = BraceletChannelManager(user, dialog_manager.event.bot)
    referral_service = ReferralService(user, SubscriptionManager(user, bracelet_channel_manager))
    payout_calculator = PayoutCalculator(referral_service, transaction_manager)

    async def get_referral_payout_users() -> list[tuple[str, float, str]]:
        result: list[tuple[str, float, str]] = []
        for individual_payout in await payout_calculator.get_individual_payouts():
            telegram_name = await individual_payout[0].awaitable_attrs.telegram_name
            payout = individual_payout[1]
            telegram_id = await individual_payout[0].awaitable_attrs.telegram_id

            result.append(
                (
                    telegram_name,
                    payout,
                    telegram_id
                 )
            )
        return result

    result = await get_referral_payout_users()
    dialog_manager.dialog_data['referral_payout_users'] = result

    return {
        'referral_payout_users': result
    }
