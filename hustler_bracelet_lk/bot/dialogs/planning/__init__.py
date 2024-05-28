from datetime import date, timedelta

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const, Jinja

from hustler_bracelet.bot.dialogs import states
from hustler_bracelet.bot.utils.lang_utils import plural_form, represent_date
from hustler_bracelet.database.task import Task
from hustler_bracelet.managers import FinanceManager


def get_planning_data_getter(*, include_other_days: bool = True):
    async def wrapped(dialog_manager: DialogManager, **kwargs):
        finance_manager: FinanceManager = dialog_manager.middleware_data['finance_manager']

        all_tasks = await finance_manager.get_active_tasks()

        tasks_for_today = [
            task for task in all_tasks if task.planned_complete_date == date.today()
        ]
        tasks_for_today_amount = len(tasks_for_today)

        tasks_for_tomorrow = [
            task for task in all_tasks if task.planned_complete_date == date.today() + timedelta(days=1)
        ]
        tasks_for_tomorrow_amount = len(tasks_for_tomorrow)

        if include_other_days:
            other_tasks_sorted = {}
            for task in all_tasks:
                if task.planned_complete_date in [date.today(), date.today() + timedelta(days=1)]:
                    continue

                if task.planned_complete_date not in other_tasks_sorted.keys():
                    other_tasks_sorted[task.planned_complete_date] = []
                other_tasks_sorted[task.planned_complete_date].append(task)

            other_tasks_sorted = dict(sorted(other_tasks_sorted.items(), key=lambda item: item[0]))
        else:
            other_tasks_sorted = {}

        other_tasks_sorted: dict[date, list[Task]]

        return {
            'tasks': {
                f'📝 {plural_form(tasks_for_today_amount, ("задача", "задачи", "задач"))} '
                f'на сегодня': (tasks_for_today, '📝 На сегодня нет задач'),

                f'🕐 {plural_form(tasks_for_tomorrow_amount, ("задача", "задачи", "задач"))}'
                ' на завтра'
                : (tasks_for_tomorrow, '🕐 На завтра нет задач'),

                **{
                    f'📆 {plural_form(len(tasks_for_this_date), ("задача", "задачи", "задач"))} на {represent_date(date_)}': (tasks_for_this_date, '') for date_, tasks_for_this_date in other_tasks_sorted.items()
                },
            },
            'today_uncompleted_tasks_amount': await finance_manager.get_amount_of_tasks_filtered_by_planned_complete_date(
                date.today(),
                completed=False
            ),
            'tomorrow_uncompleted_tasks_amount': await finance_manager.get_amount_of_tasks_filtered_by_planned_complete_date(
                date.today() + timedelta(days=1),
                completed=False
            ),
            'uncompleted_tasks_amount': await finance_manager.get_amount_of_tasks(completed=False),
            'completed_tasks_amount': await finance_manager.get_amount_of_tasks(completed=True),
        }

    return wrapped


def get_jinja_widget_for_tasks_displaying() -> Jinja:
    return Jinja(
        '{% for category, (tasks, text_for_empty_tasks) in tasks.items() %}'
        '{% if tasks %}'
        '<b>\n{{ category }}:</b>\n'
        '{% for task in tasks %}'
        ' •  {{ task.name }}\n'
        '{% endfor %}'
        '{% else %}'
        '<b>\n{{ text_for_empty_tasks }}</b>\n'
        '{% endif %}'
        '{% endfor %}'
    )


planning_main_menu_dialog = Dialog(
    Window(
        Const(
            '✅ <b>Планирование</b>'
        ),
        get_jinja_widget_for_tasks_displaying(),
        Jinja(
            '{% if uncompleted_tasks_amount > 0 %}\n'
            '💪 У тебя {{ uncompleted_tasks_amount|plural(["задача", "задачи", "задач"]) }} к выполнению. Поворкаем?\n'
            '{% endif %}\n'
            '{% if completed_tasks_amount > 0 %}\n'
            '📊 Ты закрыл уже {{ completed_tasks_amount|plural(["задачу", "задачи", "задач"]) }}. Неплохо!\n'
            '{% endif %}'
        ),
        Start(
            text=Const('➕ Добавить задачу'),
            id='add_task',
            state=states.AddTask.MAIN
        ),
        Start(
            text=Const('✅ Выполнить задачи'),
            id='complete_some_tasks',
            state=states.CompleteSomeTasks.MAIN
        ),
        Cancel(Const('❌ Отмена')),
        state=states.Planning.MAIN,
        getter=get_planning_data_getter()
    )
)
