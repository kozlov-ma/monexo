from app import Added, Spent, SpentOverDailyBudget, SpentAllBudget, DayResults


def format_float(f: float) -> str:
    return format(f, ",.2f").replace(",", " ").replace(".00", "")


def arithmetic_error(expr: str) -> str:
    return f"Выражение <b>{expr}</b> содержит ошибку и не может быть вычислено"


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
            f" Теперь новый бюджет на день: <b>{format_float(spent.new_daily_budget)}</b>.")


def spent_all_budget(spent: SpentAllBudget) -> str:
    return (f"Потрачено <b>{format_float(spent.amount)}</b>."
            f" Больше денег нет. Добавьте средства к текущему бюджету через +СУММА"
            f" или измените его с помощью /settings")


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


def days_left_must_be_positive(input: int) -> str:
    if input == 0:
        input = 5
    return f"Количество дней должно быть положительным числом, например <b>{abs(input)}</b>"


def days_left_must_be_int() -> str:
    return f"Количество дней должно быть положительным целым числом, например <b>5</b>"


def settings_saved(budget: float, days_left: int) -> str:
    return (f"Отлично! Осталось <b>{format_float(budget)}</b> на <b>{days_left}</b> дней,"
            f" бюджет на день: <b>{format_float(budget / days_left)}</b>")


def period_ended(saved: float) -> str:
    if saved <= 1e-3:
        return "Период закончился. Начнём сначала? /settings"
    else:
        return f"Успех ! Период закончился и удалось сэкономить <b>{format_float(saved)}</b>! Начнём сначала? /settings"


def stats(day_res: DayResults) -> str:
    msg = "<b>Статистика на день:</b>\n"
    if day_res.income > 0:
        msg += f"Доходы за сегодня: <b>{format_float(day_res.income)}</b>\n"
    if day_res.expense > 0:
        msg += f"Расходы за сегодня: <b>{format_float(day_res.expense)}</b>\n"

    msg += f"Остаток на сегодня: <b>{format_float(day_res.saved)}</b>\n"
    msg += f"Остаток на <b>{format_float(day_res.new_days_left)}</b> дней: <b>{format_float(day_res.new_remaining_budget)}</b>\n"
    msg += f"Новый бюджет на день: <b>{format_float(day_res.new_daily_budget)}</b>"

    return msg


def day_results(day_res: DayResults) -> str:
    msg = "<b>Начался новый день!</b>\n"
    if day_res.income > 0:
        msg += f"Доходы за день: <b>{format_float(day_res.income)}</b>\n"
    if day_res.expense > 0:
        msg += f"Расходы за день: <b>{format_float(day_res.expense)}</b>\n"
    if day_res.saved > 0:
        msg += f"Удалось сэкономить: <b>{format_float(day_res.saved)}</b>\n"

    msg += f"Остаток на <b>{format_float(day_res.new_days_left)}</b> дней: <b>{format_float(day_res.new_remaining_budget + day_res.new_daily_budget)}</b>\n"
    msg += f"Бюджет на сегодня: <b>{format_float(day_res.new_daily_budget)}</b>"

    return msg


def help_msg() -> str:
    return """
<b>Что может этот бот?</b>
    - Помогает учитывать ежедневные расходы и строить бюджет на небольшой срок
    - В конце дня предоставляет статистику
    - Хвалит за экономию

<b>Начало работы</b>
    - Чтобы указать срок и бюджет, используйте /settings

<b>Доходы и расходы</b>
    - Чтобы записать трату, просто отправьте боту число, например <b>1000</b>
    - Для записи трат можно использовать арифметические выражения, например <b>1000 + 500 * 2</b> или <b>600 / 5</b>
    - Чтобы записать пополнение, используйте число со знаком '<b>+</b>', например <b>+1000</b>

<b>Что дальше?</b>
    - Посмотреть статистику на сегодня можно с помощью /stats
    - Каждые 24 часа бот будет сообщать вам о текущем состоянии бюджета и давать статистику за прошедший день
    - Если вы считаете, что новые траты относятся к следующему дню, используйте /nextday
    - Это сообщение можно показать ещё раз с помощью /help
"""


def test_format():
    assert format_float(1.2345) == "1.23"
    assert format_float(1.2) == "1.20"
    assert format_float(1) == "1"
    assert format_float(1000000) == "1 000 000"
    assert format_float(1000000.1) == "1 000 000.10"
