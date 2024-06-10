from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from hustler_bracelet_lk.bot.dialogs.main.states import MainDialogState
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager
from hustler_bracelet_lk.subscription.subscription_manager import SubscriptionManager
from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager
from hustler_bracelet_lk.repos.user import user_repository
from hustler_bracelet_lk.repos.bracelet_transaction import bracelet_transaction_repository


async def start_command_handler(message: Message, dialog_manager: DialogManager):
    # if dialog_manager.middleware_data['user_created']:
    #     await dialog_manager.start(MainDialogState.MAIN)  # TODO: onboarding
    #     return

    possible_referral_id = message.text.removeprefix('/start').strip()
    if possible_referral_id:
        dialog_manager.middleware_data['referred_by'] = possible_referral_id

    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(MainDialogState.MAIN, mode=StartMode.RESET_STACK)


async def approve_command_handler(message: Message, dialog_manager: DialogManager):
    telegram_id = message.text.removeprefix('/approve ').strip()
    if not telegram_id:
        await message.answer('нет таких')

    user = user_repository.get_by_pk(telegram_id)
    bracelet_channel_manager = BraceletChannelManager(user, message.bot)
    subscription_manager = SubscriptionManager(user, bracelet_channel_manager)
    transaction_manager = TransactionManager(user)

    all_transactions = await bracelet_transaction_repository.filter()
