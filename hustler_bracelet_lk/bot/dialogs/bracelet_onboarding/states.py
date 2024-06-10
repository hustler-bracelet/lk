from aiogram.fsm.state import State, StatesGroup


class BraceletOnboardingState(StatesGroup):
    MAIN = State()
    CRYPTO = State()
    NETWORKING = State()
    HEALTH = State()
    JOBS = State()
    ARTICLES = State()
    HELPER_BOT = State()
    ACTIVITIES = State()
    FINAL = State()

    SUBSCRIPTION_MAIN = State()
    SUBSCRIPTION_FINAL = State()
