from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Start, SwitchTo, Cancel, Row, Back, Group, Button
from .states import BraceletOnboardingState


async def on_next_clicked(callback: ChatEvent, _, manager: DialogManager, **kwargs):
    # чтобы бот не зависал при попытке тыкнуть "далее" в конце стека.
    # не должно вызываться, потому что в конце стека нет кнопки "далее",
    # но полеть имезно
    # блять, иметь полезно
    try:
        await manager.next()
    except IndexError:
        await callback.answer('я запрещаю')


async def on_payment_proof_sent(
        message: Message,
        _: MessageInput,
        dialog_manager: DialogManager
):
    await message.forward(chat_id=6567176437)  # TODO: change to ambi
    dialog_manager.dialog_data['payment_message'] = message.model_copy()
    return await dialog_manager.next()


# виджет с кнопками галереи (назад, далее, о да я возбудился и хочу купить подписку)
gallery_control_widget = Group(
    Row(
        Back(Const('⬅️ Назад')),
        Button(Const('➡️ Далее'), id='lk.bracelet_onboarding.next_btn', on_click=on_next_clicked)
    ),
    Start(
        text=Const('✅ Перейти к оформлению'),
        id='lk.bracelet_onboarding.subscription_flow_btn',
        state=BraceletOnboardingState.SUBSCRIPTION_MAIN
    )
)


# этот диалог надо по-хорошему распилить
bracelet_onboarding_dialog = Dialog(

    # --- ГЛАВНОЕ МЕНЮ ---

    Window(
        Const(
            '⌚️ <b>Что ты хочешь получить от HUSTLER BRACELET?</b>\n'
            '\n'
            '<b>HUSTLER BRACELET</b> — продукт, меняющий будущее. \n'
            'Получи доступ к тоннам обучалок по всем направлениям, прибыльной работе '
            'для любой ниши, созвонам и индивидуальным разборам кейсов, '
            'программам тренировок, реферальной системе, боту для планирования и систематизации '
            'своей жизни, и многому другому...'
        ),

        SwitchTo(
            text=Const('🪙 Криптовалюта'),
            id='lk.bracelet_onboarding.crypto_btn',
            state=BraceletOnboardingState.CRYPTO
        ),
        SwitchTo(
            text=Const('👥 Общение, связи, нетворкинг'),
            id='lk.bracelet_onboarding.networking_btn',
            state=BraceletOnboardingState.NETWORKING
        ),
        SwitchTo(
            text=Const('🏃‍♂️ Здоровье и спорт'),
            id='lk.bracelet_onboarding.health_btn',
            state=BraceletOnboardingState.HEALTH
        ),
        SwitchTo(
            text=Const('💼 Работа и заказы'),
            id='lk.bracelet_onboarding.jobs_btn',
            state=BraceletOnboardingState.JOBS
        ),
        SwitchTo(
            text=Const('📝 Статьи и обучалки'),
            id='lk.bracelet_onboarding.articles_btn',
            state=BraceletOnboardingState.ARTICLES
        ),
        SwitchTo(
            text=Const('⌚️👈 Бот HUSTLER HELPER'),
            id='lk.bracelet_onboarding.helper_bot_btn',
            state=BraceletOnboardingState.HELPER_BOT
        ),
        Cancel(Const('❌ Отмена')),

        state=BraceletOnboardingState.MAIN
    ),

    # --- ЭТАПЫ ГАЛЕРЕИ (ОНБОРДИНГА) ---

    Window(
        Const(
            '🪙 <b>Криптовалюта</b>\n'
            '\n'
            'В HUSTLER BRACELET я выкладываю свои сделки на рынке криптовалют и '
            'детально анализирую проекты. Если слушать мои коллы — подписка '
            'окупится в первую же неделю. Будь то ты новичок или уже заядлый криптан, '
            'мои посты полезны для всех, кто интересуется этой нишей.'
        ),
        gallery_control_widget,
        state=BraceletOnboardingState.CRYPTO
    ),

    Window(
        Const(
            '👥 <b>Общение, связи, нетворкинг</b>\n'
            '\n'
            'Наше комьюнити даёт возможность ребятам взаимодействовать друг с другом, '
            'создавать совместные проекты, соревноваться и развиваться вместе. \n'
            'Без полезных связей и знакомств ты не останешься.'
        ),
        gallery_control_widget,
        state=BraceletOnboardingState.NETWORKING
    ),

    Window(
        Const(
            '🏃‍ <b>Здоровье и спорт</b>\n'
            '\n'
            'Мы сотрудничаем с квалифицированным тренером и экспертом в эндокринологии '
            'ради индивидуальных программ тренировок, гайдов на БАДы и лекарства, '
            'разборов прогресса и прочих крутых штук.\n'
            'А ещё в боте HUSTLER HELPER скоро появится полноценный трекер калорий и '
            'тренировок с персональными рекомендациями.'
        ),
        gallery_control_widget,
        state=BraceletOnboardingState.HEALTH
    ),

    Window(
        Const(
            '💼‍ <b>Работа и заказы</b>\n'
            '\n'
            'Уже сейчас в браслете есть вакансии для телеграм-менеджеров, монтажёров, дизайнеров, '
            'художников, кодеров, трафферов и представителей других ниш. Опытные ребята часто ищут, '
            'кому можно делегировать свою работу, и дают шансы новичкам развиваться в этой сфере.\n'
            'Так чего ты ждёшь?'
        ),
        gallery_control_widget,
        state=BraceletOnboardingState.JOBS
    ),

    Window(
        Const(
            '📝 <b>Статьи и обучалки</b>\n'
            '\n'
            'Как наладить работу организма на гормональном уровне? '
            'Как полюбить абсолютно любую работу? Как прийти в себя после бурной ночи? '
            'Что делать, если не хватает энергии? Как контрить выгорание?\n'
            '\n'
            'В браслете тебя ждёт огромное количество подкастов, историй из личного '
            'опыта и других обучающих материалов на любую нишу: от крипты до семейных проблем.'
        ),
        gallery_control_widget,
        state=BraceletOnboardingState.ARTICLES
    ),

    Window(
        Const(
            '⌚️👈 <b>Бот HUSTLER HELPER</b>\n'
            '\n'
            'Всё ещё не можешь превратить свои движения в чёткую систему, которая работает '
            'на тебя, а не ты на неё? Твоя жизнь — это хаос, хранящийся лишь у тебя в голове?\n'
            '\n'
            'Бот HUSTLER HELPER — это трекер финансов и инвестиций, система планирования, '
            'и даже трекер спорта <i>(в недалёком будущем)</i>!\n'
            'А главное — в боте постоянно проводятся денежные активности для разных ниш!\n'
            'Выполняй задания, зарабатывай баллы, продвигайся выше в топе и '
            'выиграй денежный приз за свои старания.'
        ),
        gallery_control_widget,
        state=BraceletOnboardingState.HELPER_BOT
    ),

    Window(
        Const(
            'Думаю, ты уже понял, что HUSTLER BRACELET — это действительно <b>продукт, меняющий будущее.</b>'
        ),
        Row(
            Back(Const('⬅️ Назад')),
            Start(
                text=Const('✅ Перейти к оформлению'),
                id='lk.bracelet_onboarding.subscription_flow_btn',
                state=BraceletOnboardingState.SUBSCRIPTION_MAIN
            ),
        ),
        state=BraceletOnboardingState.FINAL
    ),

    # --- ОКНО ОПЛАТЫ ---

    Window(
        Const(
            '💵 <b>Оплата подписки</b>\n'
            '\n'
            'Говноеды на ЮКассе решили не подключать нам платёжку, поэтому пока работаем так.\n'
            'Отправь ровно <b>1 000₽</b> (или <b>$12</b>) по следующим реквизитам:\n'
            '\n'
            '💳 Банковская карта: <code>2202 2063 0820 3566</code>\n'
            '💲 USDT (BEP20): <code>0x7a3d724154d85fa34eb9569fa25e8dc1ec4a9feb</code>\n'
            '✈️ TON: <code>UQCTn5yZ16TP16kxhXU5IRDmU-zf09s-dKl__HPUC1K0b4OZ</code>\n'
            '\n'
            'После оплаты отправь сюда скриншот с подтверждением оплаты. В комментариях к '
            'платежу напиши свой ник в телеграме.'
        ),
        MessageInput(on_payment_proof_sent, [ContentType.PHOTO]),
        Cancel(Const('❌ Отмена')),
        state=BraceletOnboardingState.SUBSCRIPTION_MAIN
    ),

    # --- ОКНО УСПЕШНОЙ ОПЛАТЫ ---

    Window(
        Format(
            '✅ <b>Готово!</b>\n'
            '\n'
            'Лови ссылку на канал HUSTLER BRACELET 👉 https://t.me/+0WrsTkoo5r81ZjY6.\n'
            'Подай туда заявку. После того, как админ проверит твой скриншот, он примет заявку '
            'на вступление.\n'
            '\n'
            'Фарта всем! 52 🖐✌️'
        ),
        Cancel(Const('✅ Готово')),
        state=BraceletOnboardingState.SUBSCRIPTION_FINAL
    )
)
