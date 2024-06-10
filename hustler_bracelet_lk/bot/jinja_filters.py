import datetime
from typing import Callable

from aiogram import types, html
from aiogram_dialog import DialogManager


def format_number(number: float) -> str:
    number = round(number, 1)
    if not isinstance(number, int):
        if number.is_integer():
            number = int(number)

    return f'{number:_}'.replace('_', ' ')  # КОСТЫЛИ ЕБУЧИЕ


def format_money_amount(money_amount: float) -> str:
    base = f'{format_number(money_amount)}₽'

    rounded_money_amount = round(money_amount)
    if rounded_money_amount == 52:
        base += ' 🖐✌️'
    elif rounded_money_amount == 228:
        base += ' 💊'
    elif rounded_money_amount in (1337, 420):
        base += ' 😮‍💨'
    elif rounded_money_amount == 100_000:
        base += ' 🥳'
    elif rounded_money_amount == 1488:
        base += ' 📀'

    return base


async def event_value_getter(dialog_manager: DialogManager, **kwargs):
    return {
        'value': dialog_manager.dialog_data['value']
    }


def plural_form(number: int, titles: tuple[str, ...] | list[str], include_number: bool = True, do_format_number: bool = True):
    """
    :param include_number:
    :param number:
    :param titles: 1 Минута, 2 минуты, 0 минут
    :return:
    """

    cases = [2, 0, 1, 1, 1, 2]

    if 4 < number % 100 < 20:
        idx = 2
    elif number % 10 < 5:
        idx = cases[number % 10]
    else:
        idx = cases[5]

    title = titles[idx]
    if include_number:
        return f'{format_number(number)} {title}'
    return title


def represent_date(date: datetime.date) -> str:
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

    today = datetime.date.today()

    date_representation = f'{date.day} {months[date.month - 1]}'

    if date.year != today.year:
        date_representation += f' {date.year}'

    return date_representation


def represent_datetime(datetime: datetime.datetime) -> str:
    return f'{represent_date(datetime.date())} ({datetime.time().strftime("%H:%M")} МСК)'


def get_jinja_filters() -> dict[str, Callable[..., str]]:
    return {
        'plural': plural_form,
        'date': represent_date,
        'datetime': represent_datetime,
        'money': format_money_amount,
        'number': format_number,
        'debug': print,
    }
