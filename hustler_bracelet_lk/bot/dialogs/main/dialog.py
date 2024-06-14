from aiogram_dialog import Dialog, Window, LaunchMode, DialogManager
from aiogram_dialog.widgets.text import Format, Const, Case, Jinja
from aiogram_dialog.widgets.kbd import Start
from magic_filter import F

from .getters import main_dialog_getter
from .states import MainDialogState
from enum import Enum, auto

from ..bracelet_onboarding.states import BraceletOnboardingState
from ..referral.states import ReferralState
from ..referral_payout.states import ReferralPayoutState


class BraceletCase(Enum):
    INACTIVE = auto()
    ACTIVE = auto()


class ReferralCase(Enum):
    NOT_SHOWING = auto()
    NO_REFERRED_USERS = auto()
    REFERRAL_ACTIVE = auto()


active_subscription_widget = Jinja(
    '<b>✅ Подписка на HUSTLER BRACELET активна.</b>\n'
    '🗓 <b>До:</b> {{ bracelet_will_end_on|datetime }}'
)

inactive_subscription_widget = Format(
    '❌ <b>У тебя ещё нет подписки на HUSTLER BRACELET.</b>\n'
    'А жаль — ты многое упускаешь!'
)

no_referred_users_widget = Const(
    '\n👥 <b>Ты ещё не привёл ни одного реферала!</b>\n'
    'Приводи друзей в браслет и получай рубли, а не циферки!'
)

referral_active_widget = Jinja(
    '\n👥 <b>Рефералов приведено:</b> {{ referred_users_amount }}\n'
    '💸 <b>Твоя выплата:</b> {{ referral_payout_rub|money }}'
)

will_end_soon_widget = Const(
    '❗️ <b>Твоя подписка скоро закончится!</b> Успей продлить по кнопке ниже 👇',
    when=F['will_end_soon']
)


def bracelet_selector(data: dict, case: Case, manager: DialogManager):
    if data['is_bracelet_active']:
        return BraceletCase.ACTIVE
    else:
        return BraceletCase.INACTIVE


def referral_selector(data: dict, case: Case, manager: DialogManager):
    if not data['is_bracelet_active']:
        return ReferralCase.NOT_SHOWING

    if data['referred_users_amount'] <= 0:
        return ReferralCase.NO_REFERRED_USERS

    return ReferralCase.REFERRAL_ACTIVE


main_dialog = Dialog(
    Window(
        Const('👋 <b>Привет, хаслер!</b>\n'),

        Case(
            texts={
                BraceletCase.ACTIVE: active_subscription_widget,
                BraceletCase.INACTIVE: inactive_subscription_widget
            },
            selector=bracelet_selector
        ),
        Case(
            texts={
                ReferralCase.NOT_SHOWING: Const(''),
                ReferralCase.NO_REFERRED_USERS: no_referred_users_widget,
                ReferralCase.REFERRAL_ACTIVE: referral_active_widget
            },
            selector=referral_selector
        ),
        will_end_soon_widget,

        Start(
            text=Const('💸 Продлить подписку'),
            id='lk.main.extend_subscription_btn',
            state=BraceletOnboardingState.SUBSCRIPTION_MAIN,
            when=F['will_end_soon']
        ),
        Start(
            text=Const('💸 Оформить подписку'),
            id='lk.main.bracelet_onboarding_btn',
            state=BraceletOnboardingState.MAIN,
            when=~F['is_bracelet_active']
        ),
        Start(
            text=Const('👥 Реферальная система'),
            id='lk.main.referral_btn',
            state=ReferralState.MAIN,
            when=F['is_bracelet_active']
        ),
        Start(
            text=Const('⚙️ Админ: Выплата по рефералке'),
            id='lk.main.referral_payout',
            state=ReferralPayoutState.MAIN,
            when=F['is_ambi']
        ),

        state=MainDialogState.MAIN
    ),
    getter=main_dialog_getter,
    launch_mode=LaunchMode.ROOT  # потому что это главное меню
)
