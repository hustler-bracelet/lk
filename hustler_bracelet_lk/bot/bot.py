import asyncio
import logging

import aiogram_dialog
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, Message, ReplyKeyboardRemove, LabeledPrice, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram_dialog import DialogManager, setup_dialogs, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownIntent
from aiogram_dialog.widgets.text import setup_jinja

import config
from .dialogs import states


async def start(message: Message, dialog_manager: DialogManager):
    await message.bot.send_invoice(
        chat_id=message.chat.id,
        title='HUSTLER BRACELET - 1 месяц подписки',
        description="""⌚👈🏻 HUSTLER BRACELET — продукт, меняющий будущее. 

Получи доступ к тоннам обучалок по всем направлениям, работе для любой ниши, созвонам и индивидуальным разборам кейсов, программам тренировок, реферальной системе, боту для планирования и систематизации своих движений, постоянным активностям с гарантированными выплатами — и гораздо большему...

Процент с каждой оплаты ежемесячно отправляем на благотворительность.""",
        payload='payload',
        provider_token='381764678:TEST:85741',
        currency='RUB',
        prices=[LabeledPrice(label='label', amount=100000)],
        photo_url='https://i.postimg.cc/nzCRrbwD/bracelet.png'
    )


async def get_more(message: Message, dialog_manager: DialogManager):
    await message.reply(
        """🤔 <b>Что такое HUSTLER BRACELET?</b>

<b>📞 Групповые созвоны</b>: Зовем гостей из самых разных ниш и перенимаем их опыт, индивидуально разбираем каждого участника

<b>💰 Крипта</b>: Мои сделки на рынке криптовалют и детальный анализ проектов 

<b>👥 Коннекты</b>: Даем возможность ребятам взаимодействовать друг с другом, создавать совместные проекты и развиваться

<b>📝 Статьи</b>: Обучающие статьи на самые разные направления и ниши 

<b>💪 Спорт</b>: Программы тренировок, консультации от профессионального тренера и контент по здоровью. 

<b>✅ Бот HUSTLER HELPER</b>: Планирование и систематизация твоих движений, калькулятор финансов и постоянные денежные активности""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Перейти к оплате (1000₽)', callback_data='amogus')]
            ]
        )
    )


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
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


# TODO: Сделать хендлинг необработанных ошибок


dialog_router = Router()

# dialog_router.include_routers(
#     # ...
# )


def setup_dp():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.register(start, F.text == "/start")
    dp.message.register(get_more, F.text == "/info")
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )

    # dp.message.middleware.register(database_middleware)
    # dp.callback_query.middleware.register(database_middleware)
    # dp.errors.middleware.register(database_middleware)
    #
    # dp.message.filter(SubChecker())

    dp.include_router(dialog_router)

    setup_dialogs(dp)

    return dp


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.TG_BOT_TOKEN, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    async def process_successful_payment(message: types.Message):
        print('successful_payment')
        await bot.send_message(
            message.chat.id,
            f'Пасиба за бабки, побрил как хомяка'
        )

    dp = setup_dp()

    dp.pre_checkout_query.register(process_pre_checkout_query)
    dp.message.register(process_successful_payment, F.successful_payment)

    # aiogram_dialog.widgets.text.jinja.default_env = setup_jinja(dp, filters=get_jinja_filters())

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
