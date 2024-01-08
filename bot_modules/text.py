from typing import Iterable

import domain
from app import Added, Spent, SpentOverDailyBudget, SpentAllBudget, DayResults, PeriodEnded


def format_float(f: float) -> str:
    return format(f, ",.2f").replace(",", " ").replace(".00", "")


def arithmetic_error(expr: str) -> str:
    if '\n' in expr:
        return f"Выражение\n\n<b>{expr}</b>\n\nсодержит ошибку и не может быть вычислено."
    return f"Выражение <b>{expr}</b> содержит ошибку и не может быть вычислено."


def cannot_spend_zero_sum() -> str:
    return "Нельзя добавить/потратить нулевую сумму."


def must_have_settings_first() -> str:
    return "Сначала введите бюджет и срок с помощью /settings"


def cannot_enter_negative_sum(sum: float) -> str:
    return (f"Введена отрицательная сумма: <b>{format_float(sum)}</b>."
            f" Если хотите потратить деньги, введите положительное число,"
            f" например <b>{format_float(abs(sum))}</b>")


def added_money(added: Added) -> str:
    return (f"Добавлено <b>{format_float(added.amount)}</b>."
            f" Теперь на сегодня доступно <b>{format_float(added.new_budget_today)}</b>")


def spent_money(spent: Spent) -> str:
    return (f"Потрачено <b>{format_float(spent.amount)}</b>."
            f" Остаток на сегодня: <b>{format_float(spent.new_budget_today)}</b>")


def spent_over_daily_budget(spent: SpentOverDailyBudget) -> str:
    return (f"Потрачено <b>{format_float(spent.amount)}</b>."
            f" Остаток на сегодня: <b>{0}</b>."
            f" Теперь новый дневной бюджет: <b>{format_float(spent.new_daily_budget)}</b>.")


def spent_all_budget(spent: SpentAllBudget) -> str:
    return (f"Потрачено <b>{format_float(spent.amount)}</b>." + no_more_money())


def no_more_money() -> str:
    return f"<b>Больше денег нет.</b> Добавьте средства к текущему бюджету через +СУММА (например, <b>+100</b>) или измените его с помощью /settings"


def ask_for_budget() -> str:
    return "Сколько денег вы хотите потратить? Введите число, например <b>1000</b> или <b>1000.50</b>"


def big_numbers_format_hint() -> str:
    return "Подсказка: длинные числа можно вводить в подобном формате: <b>10_000</b>"


def ask_for_days_left() -> str:
    return "На какой срок вы планируете бюджет? Введите количество дней, например <b>5</b>"


def budget_must_be_float() -> str:
    return "Введите число, например <b>1000</b> или <b>1000.50</b>"


def budget_must_be_positive(amount: float) -> str:
    if amount == 0:
        amount = 1000
    return f"Бюджет должен быть положительным числом, например <b>{format_float(abs(amount))}</b>"


def budget_too_big(amount: float) -> str:
    return f"Вы указали <b>слишком большой</b> бюджет. Укажите бюджет поменьше, например <b>{str(int(amount))[:10]}</b>"


def days_left_must_be_positive(input: int) -> str:
    if input == 0:
        input = 5
    return f"Количество дней должно быть положительным числом, например <b>{abs(input)}</b>"


def days_left_must_be_int() -> str:
    return f"Количество дней должно быть положительным целым числом, например <b>5</b>"


def ask_for_timezone() -> str:
    return f"Введите Ваш часовой пояс по <b>московскому</b> времени. Например, для Свердловской области он будет <b>2</b>, а для Калининградской области — <b>-1</b> или <b>23</b>"


def timezone_must_be_integer() -> str:
    return f"Часовой пояс должен быть целым числом от <b>-23</b> до <b>23</b>."


def settings_saved(budget: float, days_left: int) -> str:
    return (f"Отлично! Осталось <b>{format_float(budget)}</b> на <b>{days_left}</b> дней."
            f"Бюджет на день: <b>{format_float(budget / days_left)}</b>")


def settings_message(user: domain.User, timezone: domain.UserTimezoneInfo | None,
                     categories: list[domain.Category] | None):
    return f"""<b>Настройки</b>
Бюджет: <b>{user.remaining_budget}</b>
Дней осталось: <b>{user.days_left}</b>
Остаток на сегодня: <b>{user.budget_today}</b>
Часовой пояс: <b>{f"МСК+{timezone.timezone}" if timezone is not None else "не указан"}</b>

Категории:
<b>{
    "\n".join([" - " + category.name for category in categories])
    if categories is not None and len(categories) != 0
    else "не указаны"
    }</b>
"""


def budget_saved(budget: float):
    return f"Отлично! Бюджет сохранен: <b>{format_float(budget)}</b>"


def days_left_saved(days_left: int):
    return f"Отлично! Количество дней сохранено: <b>{days_left}</b>"


def timezone_saved(timezone: int):
    return f"Отлично! Часовой пояс сохранен: <b>МСК+{timezone}</b>"


def autoupdate_enabled() -> str:
    return f"Автообновление включено"


def autoupdate_disabled() -> str:
    return f"Автообновление выключено"


def too_many_categories() -> str:
    return ("<b>Предупреждение:</b> <i>большое количество категорий может сделать использование бота страшным и "
            "неудобным!</i>")


def underscore_in_category_name() -> str:
    return "<b>Название категории не должно содержать символ '_'.</b> Введите категории заново:"


def no_categories_msg() -> str:
    return "<b>Список категорий пуст.</b>"


def categories_msg(categories: Iterable[str]) -> str:
    return f"<b>Пользовательские категории</b>:\n" + "\n".join(categories)


def ask_for_categories() -> str:
    return ("<b>Редактирование категорий</b>\nВведите названия <b>всех</b> категорий, каждое с новой строки, "
            "например:\n\nЕда\nТранспорт\nРазвлечения\n\nЕсли хотите удалить все категории, введите '_'")


def categories_set(created: Iterable[str], removed: Iterable[str], unchanged: Iterable[str]) -> str:
    msg = ""
    created = list(created)
    removed = list(removed)
    unchanged = list(unchanged)
    if len(created) > 0:
        msg += f"<b>Добавлены следующие категории</b>:\n" + "\n".join("  + " + c for c in created) + "\n"
    if len(removed) > 0:
        msg += "<b>Удалены следующие категории</b>:\n" + "\n".join("  - " + c for c in removed) + "\n"
        if len(created) == 0 and len(unchanged) == 0:
            msg += "\n<b>Список категорий очищен.</b>\n"
    if len(unchanged) > 0:
        msg += "<b>Следующие категории не изменились</b>:\n" + "\n".join("  = " + c for c in unchanged) + "\n"

    if len(created) + len(removed) + len(unchanged) == 0:
        msg = "<b>Список категорий очищен.</b>\n"

    return msg


def cat_stats(expense_by_categories: dict[str, float]) -> str:
    msg = "<b>Расходы по категориям:</b>\n"
    for category, expense in expense_by_categories.items():
        if expense < 0.01:
            continue
        msg += f"{category}: {format_float(expense)}\n"

    return msg


def stats(day_res: DayResults) -> str:
    msg = "<b>Статистика на день:</b>\n"
    add_line = False
    if day_res.income > 0:
        msg += f"Доходы за сегодня: <b>{format_float(day_res.income)}</b>\n"
        add_line = True
    if day_res.expense > 0:
        msg += f"Расходы за сегодня: <b>{format_float(day_res.expense)}</b>\n"
        add_line = True
    if add_line:
        msg += "\n"

    if day_res.saved >= 1e-2 or day_res.new_remaining_budget >= 1e-2:
        msg += f"Остаток на сегодня: <b>{format_float(day_res.saved)}</b>\n"
        if day_res.new_days_left > 1:
            msg += f"Остаток на <b>{format_float(day_res.new_days_left)}</b> дней: <b>{format_float(day_res.new_remaining_budget)}</b>\n"
    else:
        msg += no_more_money()

    msg += "\n"

    if (day_res.expense > 0 or day_res.income > 0) and day_res.new_daily_budget >= 1e-2:
        msg += f"Новый дневной бюджет: <b>{format_float(day_res.new_daily_budget)}</b>"
        msg += "\n"

    return msg


def day_results(day_res: DayResults) -> str:
    msg = "<b>Начался новый день!</b>\n"

    add_line = False
    if day_res.income > 0:
        msg += f"Доходы за вчера: <b>{format_float(day_res.income)}</b>\n"
        add_line = True
    if day_res.expense > 0:
        msg += f"Расходы за вчера: <b>{format_float(day_res.expense)}</b>\n"
        add_line = True
    if day_res.saved > 0:
        msg += f"Удалось сэкономить: <b>{format_float(day_res.saved)}</b>\n"
        add_line = True
    if add_line:
        msg += "\n"

    if day_res.new_days_left > 1:
        msg += f"Остаток на <b>{format_float(day_res.new_days_left)}</b> дней: <b>{format_float(day_res.new_remaining_budget + day_res.new_daily_budget)}</b>\n"

    if day_res.new_daily_budget >= 1e-2:
        msg += f"Бюджет на сегодня: <b>{format_float(day_res.new_daily_budget)}</b>"
    else:
        msg += no_more_money()

    msg += "\n"

    return msg


def period_ended(p: PeriodEnded) -> str:
    msg = "<b>Статистика на день:</b>\n"

    if p.income > 0:
        msg += f"Доходы за сегодня: <b>{format_float(p.income)}</b>\n"
    if p.expense > 0:
        msg += f"Расходы за сегодня: <b>{format_float(p.expense)}</b>\n"

    msg += "\n"
    if p.saved <= 1e-3:
        msg += "<b>Период закончился.</b> Начнём сначала? /settings"
    else:
        msg += f"<b>Успех!</b> Период закончился и удалось сэкономить <b>{format_float(p.saved)}</b>! Начнём сначала? /settings"

    return msg


def telemetry(n_active_users: int, n_categories_users: int, avg_budget: float) -> str:
    msg = "<b>Общая статистика бота:</b>\n"
    msg += "\n"
    msg += f"<b>Всего активных пользователей:</b> {n_active_users}\n"
    msg += f"<b>Пользуются функцией 'Категории':</b> {n_categories_users}\n"
    msg += f"<b>Средний бюджет пользователя:</b> {avg_budget}"

    return msg


def help_msg() -> str:
    return """
<b>Настройки</b>
    - Чтобы указать срок и бюджет, используйте /settings. Также вы можете единожды указать часовой пояс для своевременного получения статистики за день

<b>Доходы и расходы</b>
    - Чтобы записать трату, просто отправьте боту число, например <b>1000</b>
    - Для записи трат можно использовать арифметические выражения, например <b>1000 + 500 * 2</b> или <b>600 / 5</b>
    - Чтобы записать пополнение, используйте число со знаком '<b>+</b>', например <b>+1000</b>

<b>Что дальше?</b>
    - Посмотреть статистику на сегодня можно с помощью /stats
    - Каждые 24 часа бот будет сообщать вам о текущем состоянии бюджета и давать статистику за прошедший день

<b>Продвинутые фичи: Категории</b>
    - Чтобы просмотреть или редактировать категории, используйте /categories или /settings
    - Если задана хотя бы одна категория, её можно будет указать при трате
    - Категории учитываются в статистике за день
    - Если вы хотите отменить выбор категории для конкретной траты, нажмите на неё ещё раз

<b>Небольшие советы</b>
    - Не обязательно записывать точную сумму траты, даже приблизительная поможет оценить, сколько вы тратите
    - Если забыли записать трату — ничего страшного!
    - Не стоит использовать Monexo как домашнюю бухгалтерию

<b>Мне не нравится бот</b>
    - Ничего страшного, всегда можно написать /stop!
"""


def you_have_to_be_admin():
    from random import choice
    messages = [
        "<b>uuyccyycocuu kuuc  yfyoff yfk uckfouckcf oco ucf c  yuf uc ofuoufuyyuckuyu!</b>",
        "<b>Детям вход воспрещён.</b>",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "<b>Мальчик, ты кто?</b>",
        "<b>18+, тебе ещё нельзя</b>",
        "<b>Admins only</b>",
        "<b>Нет.</b>"
    ]

    msg = choice(messages)
    return msg


def cancelled():
    return "<b>Отменено.</b> Теперь можно пользоваться ботом как обычно"


def cancelled_for_callback():
    return "Отменено"


def confirm_stop():
    return "<b>Вы точно хотите выключить бота?</b>"


def stop_msg():
    return ("<b>Бот отключен.</b> Все Ваши данные удалены.\nНачать пользоваться ботом ещё раз можно с помощью "
            "/settings.\nПожалуйста, отметьте, почему Вы перестали пользоваться ботом")


def thanks_for_review():
    return "<b>Спасибо за Ваш отзыв!</b> Больше Вас не побеспокоим"


def test_format():
    assert format_float(1.2345) == "1.23"
    assert format_float(1.2) == "1.20"
    assert format_float(1) == "1"
    assert format_float(1000000) == "1 000 000"
    assert format_float(1000000.1) == "1 000 000.10"


def current_timezone(timezone: int):
    return f"Ваш часовой пояс —  Msk {'+' if timezone > 0 else '-'} {timezone}."


def settings_with_time_saved(autoupdate: bool, timezone: int, budget: float, days_left: int) -> str:
    return (
        f"Отлично! Осталось <b>{format_float(budget)}</b> на <b>{days_left}</b> дней, ваш часовой пояс —  Msk {'+' if timezone > 0 else '-'} {timezone}. Ежедневное обновление {'включено' if autoupdate else 'выключено'}."
        f" бюджет на день: <b>{format_float(budget / days_left)}</b>")
