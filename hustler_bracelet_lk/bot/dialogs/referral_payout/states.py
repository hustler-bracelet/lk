from aiogram.fsm.state import State, StatesGroup


class ReferralPayoutState(StatesGroup):
    MAIN = State()
    FINAL = State()
