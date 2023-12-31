import logging
import re
import re
import uuid
from dataclasses import replace

import loguru
import option
from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery, )
from option import Option

import app.state
import domain
from bot_modules import text, kb

budget_change_router = Router()

MATH_REGEX = re.compile(r"^[+\-\d](\s?[-+/*]?\s?[._\d]+\s?(\._\d+)?)*$", re.A)
SINGLE_OPERAND_REGEX = re.compile(f"^[+\-]\d+$", re.A)


@budget_change_router.message()
async def budget_change(message: Message) -> None:
    sender_id = message.from_user.id
    if len(message.text) >= 200:
        await message.answer("<b>Сообщение слишком длинное.</b>")
    try:
        assert MATH_REGEX.match(message.text.replace("_", ""))
        result = eval(message.text.replace("_", ""))
    except Exception as e:
        await message.answer(text.arithmetic_error(message.text), parse_mode="HTML")
        return

    amount = abs(result)
    if abs(result) > 55_000_000:
        await message.answer(f"Введено слишком большое число, введите не более <b>{text.format_float(50_000_000)}</b>")
        return

    if abs(result) <= 1e-3:
        await message.answer(text.cannot_spend_zero_sum(), parse_mode="HTML")
        return

    if SINGLE_OPERAND_REGEX.match(message.text) and result > 0:
        change = (await app.add_income(sender_id, amount)).unwrap_or(None)
        if change is None:
            await message.answer(text.must_have_settings_first(), parse_mode="HTML")
            return
        msg = await message.answer(text.added_money(change), parse_mode="HTML")
        bc = (await app_bc_to_domain_bc(sender_id, msg.message_id, change)).unwrap_or(None)  # FIXME BUDGETCHANGE

        if bc is None:
            return

        await app.state.get().bc_repo.add_budget_change(bc)  # FIXME BUDGETCHANGE
    else:
        if not SINGLE_OPERAND_REGEX.match(message.text) and result < 0:
            await message.answer(text.cannot_enter_negative_sum(result), parse_mode="HTML")
            return
        else:
            change = (await app.add_expense(sender_id, amount)).unwrap_or(None)
            match change:
                case app.Spent():
                    expense_categories = await kb.categories_for_expense(sender_id, message.message_id, change.amount)
                    msg = await message.answer(text.spent_money(change), parse_mode="HTML",
                                               reply_markup=expense_categories)
                    bc = (await app_bc_to_domain_bc(sender_id, msg.message_id, change)).unwrap()  # FIXME BUDGETCHANGE
                    await app.state.get().bc_repo.add_budget_change(bc)  # FIXME BUDGETCHANGE
                case app.SpentOverDailyBudget():
                    expense_categories = await kb.categories_for_expense(sender_id, message.message_id, change.amount)
                    msg = await message.answer(text.spent_over_daily_budget(change), parse_mode="HTML",
                                               reply_markup=expense_categories)
                    bc = (await app_bc_to_domain_bc(sender_id, msg.message_id, change)).unwrap()  # FIXME BUDGETCHANGE
                    await app.state.get().bc_repo.add_budget_change(bc)  # FIXME BUDGETCHANGE
                case app.SpentAllBudget():
                    expense_categories = await kb.categories_for_expense(sender_id, message.message_id, change.amount)
                    msg = await message.answer(text.spent_all_budget(change), parse_mode="HTML",
                                               reply_markup=expense_categories)
                    bc = (await app_bc_to_domain_bc(sender_id, msg.message_id, change)).unwrap()  # FIXME BUDGETCHANGE
                    await app.state.get().bc_repo.add_budget_change(bc)  # FIXME BUDGETCHANGE
                case None:
                    await message.answer(text.must_have_settings_first(), parse_mode="HTML")
                    return
                case _:
                    raise ValueError(f"Unknown change type: {type(change)}")
            app.state.get().telemetry.int_values["Expenses tracked"] += 1

async def app_bc_to_domain_bc(user_id: int, msg_id: int, app_bc: app.BudgetChange) -> Option[
    domain.BudgetChange]:  # FIXME BUDGETCHANGE
    cat_id = None
    match app_bc:
        case app.Spent(amount, _):
            value = amount
        case app.SpentOverDailyBudget(amount, _):
            value = amount
        case app.SpentAllBudget(amount):
            value = amount
        case _:
            return Option.NONE()

    return option.Some(domain.BudgetChange(msg_id, user_id, cat_id, msg_id, value))


@budget_change_router.callback_query(
    lambda c: c.data.split("_")[0] == "bc" and len(c.data.split("_")) == 2)  # FIXME BUDGETCHANGE
async def budget_change_callback(cq: CallbackQuery) -> None:
    try:
        _, cat_id = cq.data.split("_")  # FIXME BUDGETCHANGE
        cat_id = int(cat_id)
        msg_id = cq.message.message_id
        old_bc = await app.state.get().bc_repo.get_budget_changes_by_message_id(msg_id)
        if old_bc.is_some:
            old_bc = old_bc.unwrap()
            if old_bc.category_id == cat_id:
                new_bc = replace(old_bc, category_id=None)
            else:
                new_bc = replace(old_bc, category_id=cat_id)
        else:
            await cq.message.edit_reply_markup(reply_markup=None)
            await cq.answer("Нельзя выбрать категорию для этой траты")
            return

        await app.state.get().bc_repo.update_budget_change(new_bc)

        new_kb = await kb.categories_for_expense(cq.from_user.id, msg_id, old_bc.value)  # FIXME BUDGETCHANGE
        await cq.message.edit_reply_markup(reply_markup=new_kb)
        await cq.answer("Успех")

        app.state.get().telemetry.int_values["Category used"] += 1

    except Exception as e:
        await cq.answer("Произошла ошибка..")
        logging.exception(e)
        return
