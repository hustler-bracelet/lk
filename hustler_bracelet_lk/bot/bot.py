import asyncio
import logging
import aiogram_dialog

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter, CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, ReplyKeyboardRemove
from aiogram_dialog import DialogManager, setup_dialogs, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownIntent
from aiogram_dialog.widgets.text import setup_jinja

import config
from hustler_bracelet_lk.bot.dialogs.bracelet_onboarding.dialog import bracelet_onboarding_dialog

from hustler_bracelet_lk.bot.dialogs.main.dialog import main_dialog
from hustler_bracelet_lk.bot.dialogs.main.states import MainDialogState
from hustler_bracelet_lk.bot.dialogs.referral.dialog import referral_dialog
from hustler_bracelet_lk.bot.dialogs.referral_payout.dialog import referral_payout_dialog
from hustler_bracelet_lk.bot.handlers import start_command_handler, approve_command_handler, decline_command_handler
from hustler_bracelet_lk.bot.jinja_filters import get_jinja_filters
from hustler_bracelet_lk.bot.middlewares import database_middleware


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    # Example of handling UnknownIntent Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)

    if event.update.callback_query:
        await event.update.callback_query.answer(
            "Бот был перезапущен из-за технических работ.\n"
            "Переходим в главное меню.",
        )

        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever

    elif event.update.message:
        await event.update.message.answer(
            "Бот был перезапущен из-за технических работ.\n"
            "Переходим в главное меню.",
            reply_markup=ReplyKeyboardRemove(),
        )

    await dialog_manager.start(
        MainDialogState.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


dialog_router = Router()

dialog_router.include_routers(
    main_dialog,
    referral_dialog,
    bracelet_onboarding_dialog,
    referral_payout_dialog
)


def setup_dp():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.register(start_command_handler, CommandStart())
    dp.message.register(approve_command_handler, Command('approve'))
    dp.message.register(decline_command_handler, Command('decline'))

    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )

    dp.message.middleware.register(database_middleware)
    dp.callback_query.middleware.register(database_middleware)
    dp.errors.middleware.register(database_middleware)

    dp.include_router(dialog_router)

    setup_dialogs(dp)

    return dp


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.TG_BOT_TOKEN, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    dp = setup_dp()

    aiogram_dialog.widgets.text.jinja.default_env = setup_jinja(dp, filters=get_jinja_filters())

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
