from aiogram_dialog import Dialog, Window, LaunchMode, DialogManager
from aiogram_dialog.widgets.text import Format, Const, Case, Jinja
from aiogram_dialog.widgets.kbd import Start, Back, Cancel
from magic_filter import F

from hustler_bracelet_lk.bot.dialogs.referral.getters import referral_dialog_getter
from hustler_bracelet_lk.bot.dialogs.referral.states import ReferralState

referral_dialog = Dialog(
    Window(
        Const('👥 <b>Реферальная система</b>\n'),

        Format('🔗 <b>Твоя реферальная ссылка:</b> {referral_link}\n'),

        Jinja(
            '<b>Вот кого ты уже привёл:</b>\n'
            '{% for user in referred_users %}\n'
            '• <b>{{ user["name"] }}</b> - {{ user["joined_on"] }} - {{ user["payout"] }}₽\n'
            '{% endfor %}\n'
            '\n'
            '👥 <b>Всего приведено:</b> {{ referred_users_amount }} чел.\n'
            '💸 <b>Твоя выплата:</b> {{ referral_payout_rub }} рублей',  # TODO: jinja filter money
            when=F['referred_users_amount'] > 0
        ),

        Cancel(Const('⬅️ Назад')),

        state=ReferralState.MAIN
    ),
    getter=referral_dialog_getter
)
