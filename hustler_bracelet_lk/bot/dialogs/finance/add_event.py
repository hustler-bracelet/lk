from datetime import date
from typing import Any

from aiogram import types
from aiogram.types import CallbackQuery
from aiogram_dialog import ChatEvent, Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import (
    Calendar, ManagedCalendar, Button, Back, Cancel
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from hustler_bracelet.bot.dialogs import states
from hustler_bracelet.bot.dialogs.finance.widgets import get_choose_category_kb
from hustler_bracelet.bot.dialogs.widgets import Today, NumberInput
from hustler_bracelet.bot.utils.lang_utils import finance_event_words_getter, event_value_getter
from hustler_bracelet.managers.finance_manager import FinanceManager


async def on_start_add_event_dialog_click(start_data: dict, manager: DialogManager):
    event_type = start_data['event_type']

    finance_manager: FinanceManager = manager.middleware_data['finance_manager']
    categories_amount = await finance_manager.get_categories_amount(event_type)

    if categories_amount == 0:
        await manager.start(
            states.AddFinanceCategory.ENTER_NAME_FROM_EVENT_ADDING,
            data={
                'cat_type': manager.start_data['event_type'],
                'force_done': True
            }
        )
        return


async def on_date_clicked(
        callback: ChatEvent,
        widget: ManagedCalendar | None,
        manager: DialogManager,
        selected_date: date
):
    await callback.answer(str(selected_date))
    finance_manager: FinanceManager = manager.middleware_data['finance_manager']

    manager.dialog_data['event_date'] = selected_date  # Пригодится при форматировании финального сообщения

    category = await finance_manager.get_category_by_id(manager.dialog_data['category_id'])

    await finance_manager.add_finance_transaction(
        category,
        manager.dialog_data['value'],
        selected_date
    )

    await manager.next()


async def on_add_category_click(
        callback: types.CallbackQuery,
        button: Button,
        manager: DialogManager,
):
    await manager.start(
        state=states.AddFinanceCategory.ENTER_NAME,  # Скипаем первый этап, т.к. ответ на первый вопрос (тип категории) уже известен
        data={
            'cat_type': manager.start_data['event_type'],
            'force_done': True
        }
    )


async def on_choose_category_click(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        item_id: int
):
    manager.dialog_data['category_id'] = item_id

    await manager.next()


async def category_choose_window_getter(dialog_manager: DialogManager, **kwargs):
    finance_manager: FinanceManager = dialog_manager.middleware_data['finance_manager']
    categories = await finance_manager.get_all_categories(dialog_manager.start_data['event_type'])

    return {
        'categories': [(category.name, category.id) for category in categories]
    }


async def on_amount_for_new_event_entered(
        message: types.Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        data: float
):
    dialog_manager.dialog_data['value'] = float(data)
    await dialog_manager.next()


async def on_process_result(
        start_data: dict,
        result_data: dict,
        dialog_manager: DialogManager
):
    if result_data.get('fucked_up_on_the_category_creating', False):
        await dialog_manager.done()
        return

    dialog_manager.dialog_data['category_id'] = result_data['category_id']
    await dialog_manager.next()


add_finance_event_dialog = Dialog(
    Window(
        Format(
            '{finance_event_emoji} <b>Добавление {finance_event_name}а</b>\n'
            '\n'
            'Выбери категорию {finance_event_name}ов или создай новую:'
        ),
        get_choose_category_kb(on_choose_category_click),
        Button(text=Const('➕ Создать новую категорию'), id='add_fin_category', on_click=on_add_category_click),
        Cancel(Const('❌ Отмена')),
        state=states.AddFinanceEvent.MAIN,
        getter=category_choose_window_getter
    ),
    Window(
        Format(
            '{finance_event_emoji} <b>Добавление {finance_event_name}а</b>\n'
            '\n'
            'Введи сумму, которую ты {finance_event_verb} (в рублях):'
        ),
        NumberInput(on_success=on_amount_for_new_event_entered),
        Back(Const('⬅️ Назад')),
        state=states.AddFinanceEvent.ENTER_VALUE
    ),
    Window(
        Format(
            '{finance_event_emoji} <b>Добавление {finance_event_name}а</b>\n'
            '\n'
            'Когда ты {finance_event_verb} эти деньги?'
        ),
        Calendar(
            id='fin_calendar',
            on_click=on_date_clicked,
            # config=CalendarConfig(
            #     max_date=datetime.date.today()
            # )
        ),
        Today(on_date_clicked),
        Back(Const('⬅️ Назад')),

        state=states.AddFinanceEvent.CHOOSE_DATE,
    ),
    Window(
        Jinja(
            '{{ finance_event_emoji }} <b>Добавление {{ finance_event_name }}а</b>\n'
            '\n'
            '✅ {{ capitalized_finance_event_name }} {{ value | money }} за {{ dialog_data["event_date"] | date }} успешно зарегистрирован.'
        ),
        Cancel(Const('👌 Ок')),
        state=states.AddFinanceEvent.FINAL,
        getter=event_value_getter
    ),
    getter=finance_event_words_getter,
    on_process_result=on_process_result,
    on_start=on_start_add_event_dialog_click
)
