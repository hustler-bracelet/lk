from aiogram_dialog import DialogManager

import config
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager
from hustler_bracelet_lk.subscription.errors import UnmigratedSubscriptionError
from hustler_bracelet_lk.subscription.subscription_manager import SubscriptionManager
from hustler_bracelet_lk.referral.service import ReferralService
from hustler_bracelet_lk.referral.payout_calculator import PayoutCalculator
from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager


async def main_dialog_getter(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.middleware_data['user']
    session = dialog_manager.middleware_data['session']

    transaction_manager = TransactionManager(user, session)
    bracelet_channel_manager = BraceletChannelManager(user, dialog_manager.event.bot)
    subscription_manager = SubscriptionManager(user, bracelet_channel_manager, session)
    referral_service = ReferralService(user, subscription_manager, session)
    payout_calculator = PayoutCalculator(referral_service, transaction_manager)

    try:
        bracelet_subscription = await subscription_manager.get_user_subscription()
    except UnmigratedSubscriptionError:
        bracelet_subscription = None  # TODO XXX

    is_bracelet_active = bracelet_subscription is not None

    bracelet_will_end_on = (await bracelet_subscription.awaitable_attrs.will_end_on) if is_bracelet_active else None
    referred_users_amount = len(await referral_service.get_referred_users())
    referral_payout_rub = await payout_calculator.get_total_payout()
    is_ambi = await user.awaitable_attrs.telegram_id in config.ADMINS

    return {
        'is_bracelet_active': is_bracelet_active,
        'bracelet_will_end_on': bracelet_will_end_on,
        'referred_users_amount': referred_users_amount,
        'referral_payout_rub': referral_payout_rub,
        'is_ambi': is_ambi
    }
