from aiogram.fsm.state import State, StatesGroup


class ReferralState(StatesGroup):
    MAIN = State()
    GET_PAYOUT = State()
