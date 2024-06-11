from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from hustler_bracelet_lk.bot.dialogs.main.states import MainDialogState
from hustler_bracelet_lk.subscription.bracelet_channel_manager import BraceletChannelManager
from hustler_bracelet_lk.subscription.errors import UnmigratedSubscriptionError, UserAlreadyRemovedError
from hustler_bracelet_lk.subscription.subscription_manager import SubscriptionManager
from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager
from hustler_bracelet_lk.repos.user import user_repository
from hustler_bracelet_lk.repos.bracelet_transaction import bracelet_transaction_repository


async def start_command_handler(message: Message, dialog_manager: DialogManager):
    possible_referral_id = message.text.removeprefix('/start').strip()
    if possible_referral_id:
        possible_referral_id = int(possible_referral_id)

        if dialog_manager.middleware_data['did_create_user']:
            user = dialog_manager.middleware_data['user']
            user.referred_by = possible_referral_id
            await user_repository.update(user)
            dialog_manager.middleware_data['user'] = user

    await dialog_manager.start(MainDialogState.MAIN, mode=StartMode.RESET_STACK)


async def approve_command_handler(message: Message, dialog_manager: DialogManager):
    telegram_id = message.text.removeprefix('/approve ').strip()
    if not telegram_id:
        await message.answer('ты чо офигел')

    telegram_id = int(telegram_id)

    user = await user_repository.get_by_pk(telegram_id)
    bracelet_channel_manager = BraceletChannelManager(user, message.bot)
    subscription_manager = SubscriptionManager(user, bracelet_channel_manager)
    transaction_manager = TransactionManager(user)

    all_user_transactions = await bracelet_transaction_repository.filter_by(
        telegram_id=user.telegram_id
    )
    if not all_user_transactions:
        await message.answer('этот белый не подавал заявку')

    transaction = all_user_transactions[0]
    await transaction_manager.approve_transaction(transaction)

    if await subscription_manager.get_user_subscription():
        await subscription_manager.extend_subscription()
        await message.answer('этот белый уже был в браслете, поэтому я продлил подписку. готово')
        await message.bot.send_message(
            chat_id=await user.awaitable_attrs.telegram_id,
            text='✅ Подписка успешно продлена!'
        )
        return

    else:
        await subscription_manager.subscribe(transaction)
        await message.answer('всё, готово. прими его в канал пж')
        await message.bot.send_message(
            chat_id=await user.awaitable_attrs.telegram_id,
            text='✅ Подписка успешно оформлена! Добро пожаловать в наши ряды 🤝'
        )

        referred_by = await user.awaitable_attrs.referred_by

        if referred_by:
            await message.bot.send_message(
                chat_id=referred_by,
                text=f'🤑 Твой реферал {await user.awaitable_attrs.telegram_name} оплатил подписку!'
            )

        return


async def decline_command_handler(message: Message, dialog_manager: DialogManager):
    telegram_id = message.text.removeprefix('/decline ').strip()
    if not telegram_id:
        await message.answer('ты чо офигел')

    telegram_id = int(telegram_id)

    user = await user_repository.get_by_pk(telegram_id)
    transaction_manager = TransactionManager(user)

    all_user_transactions = await bracelet_transaction_repository.filter_by(
        telegram_id=await user.awaitable_attrs.telegram_id
    )
    if not all_user_transactions:
        await message.answer('этот белый не подавал заявку')

    transaction = all_user_transactions[0]
    await transaction_manager.decline_transaction(transaction)
    await message.answer('обломали этого мэнчика')
    await message.bot.send_message(
        chat_id=await user.awaitable_attrs.telegram_id,
        text='❌ Пруф не прошёл проверку! Пиши @ambienthugg, если считаешь, что это ошибка'
    )
    return
