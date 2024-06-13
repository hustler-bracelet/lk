import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, LaunchMode, DialogManager
from aiogram_dialog.widgets.text import Format, Const, Case, Jinja
from aiogram_dialog.widgets.kbd import Start, Back, Cancel, ScrollingGroup, Select
from magic_filter import F

from hustler_bracelet_lk.bot.dialogs.referral_payout.getters import referral_payout_dialog_getter
from hustler_bracelet_lk.bot.dialogs.referral_payout.states import ReferralPayoutState
from hustler_bracelet_lk.database import BraceletTransaction
from hustler_bracelet_lk.enums import TransactionType
from hustler_bracelet_lk.database.engine import SessionMaker
from hustler_bracelet_lk.repos.user import get_user_repository
from hustler_bracelet_lk.subscription.transaction_manager import TransactionManager


async def on_user_selector_click(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    referral_telegram_id = int(item_id)
    caller_telegram_id = dialog_manager.event.from_user.id

    session = dialog_manager.middleware_data['session']

    user_repository = get_user_repository(session)
    referral_user = await user_repository.get_by_pk(referral_telegram_id)
    caller_user = await user_repository.get_by_pk(caller_telegram_id)

    transaction_manager = TransactionManager(caller_user, session)

    def get_user_item_by_id(tg_id: int) -> tuple[str, float, str] | None:
        for item in dialog_manager.dialog_data['referral_payout_users']:
            if item[2] == referral_telegram_id:
                return item

        return None

    amount = get_user_item_by_id(referral_telegram_id)[1]

    transaction = await transaction_manager.create_pending_transaction(
        transaction_type=TransactionType.OUTCOME,
        amount=amount,
        reason=f'Выплата рефки юзеру {referral_telegram_id}'
    )
    await transaction_manager.approve_transaction(transaction)

    await dialog_manager.event.bot.send_message(
        chat_id=caller_telegram_id,
        text=f'🤑 Выплата {amount} рублей по рефералке отправлена!'
    )

    await dialog_manager.next()


referral_payout_dialog = Dialog(
    Window(
        Const('выбери пользователя, которому хочешь выплатить бабосики:'),

        ScrollingGroup(
            Select(
                Jinja('{{ item[0] }}: {{ item[1]|money }}'),
                id='lk.referral_payout.user_selector',
                item_id_getter=operator.itemgetter(2),
                items='referral_payout_users',
                on_click=on_user_selector_click
            ),
            id='lk.referral_payout.scrolling_group',
            width=1,
            height=6,
            hide_on_single_page=True
        ),

        Cancel(Const('⬅️ Назад')),

        state=ReferralPayoutState.MAIN
    ),

    Window(
        Const('успех!'),
        Cancel(Const('✅ Готово')),
        state=ReferralPayoutState.FINAL
    ),

    getter=referral_payout_dialog_getter
)
