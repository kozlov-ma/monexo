from dataclasses import replace

from app import state
from app.api_types import (
    Spent,
    Added,
    SpentOverDailyBudget,
    SpentAllBudget,
    PeriodEnded,
    DayResults,
)
from option import Result, Ok, Err
from app import errors


async def add_expense(
        user_id: int, amount: float
) -> Result[Spent | SpentOverDailyBudget | SpentAllBudget, errors.UserDoesNotExist]:
    user = (await state.get().users_repo.get_by_id(user_id)).unwrap_or(None)
    if user is None:
        return Err(
            errors.UserDoesNotExist(
                f"User {user} does not exist in the repository, therefore cannot add money"
            )
        )

    left_for_today = user.budget_today - amount
    if left_for_today > 0:
        user = replace(
            user, expense_today=user.expense_today + amount, budget_today=left_for_today
        )
        await state.get().users_repo.update_user(user)  # FIXME Result
        return Ok(Spent(amount, left_for_today))
    else:
        left_whole = user.remaining_budget - abs(left_for_today)
        if left_whole <= 0:
            user = replace(
                user,
                budget_today=0,
                expense_today=user.expense_today + amount,
                remaining_budget=0
            )

            await state.get().users_repo.update_user(user)  # FIXME result
            return Ok(SpentAllBudget(amount))

        user = replace(
            user,
            budget_today=0,
            expense_today=user.expense_today + amount,
            remaining_budget=left_whole,
        )

        await state.get().users_repo.update_user(user)  # FIXME Result
        return Ok(
            SpentOverDailyBudget(amount, user.remaining_budget / (user.days_left - 1))
        )


async def add_income(
        user_id: int, amount: float
) -> Result[Added, errors.UserDoesNotExist]:
    user = (await state.get().users_repo.get_by_id(user_id)).unwrap_or(None)
    if user is None:
        return Err(
            errors.UserDoesNotExist(
                f"User {user} does not exist in the repository, therefore cannot add money"
            )
        )

    user = replace(
        user,
        income_today=user.income_today + amount,
        budget_today=user.budget_today + amount,
    )

    await state.get().users_repo.update_user(user)  # FIXME result

    return Ok(Added(amount, user.budget_today))


async def apply_today(
        user_id: int,
) -> Result[DayResults | PeriodEnded, errors.UserDoesNotExist]:
    user = (await state.get().users_repo.get_by_id(user_id)).unwrap_or(None)
    if user is None:
        return Err(
            errors.UserDoesNotExist(
                f"User {user} does not exist in the repository, therefore cannot add money"
            )
        )

    income = user.income_today
    expense = user.expense_today
    saved = user.budget_today
    new_days_left = max(user.days_left - 1, 0)

    if new_days_left == 0:
        await state.get().users_repo.remove_user_by_id(user.id)  # FIXME result
        return Ok(PeriodEnded(income, expense, saved))

    new_remaining_budget = user.remaining_budget + saved
    new_day_budget = new_remaining_budget / new_days_left
    new_remaining_budget -= new_day_budget

    user = replace(
        user,
        income_today=0,
        expense_today=0,
        remaining_budget=new_remaining_budget,
        budget_today=new_day_budget,
        days_left=new_days_left
    )

    await state.get().users_repo.update_user(user)  # FIXME result
    await state.get().bc_repo.remove_all_budget_changes_by_tg_id(user.id)

    return Ok(
        DayResults(
            income, expense, saved, new_remaining_budget, new_day_budget, new_days_left
        )
    )


async def stats(user_id: int) -> Result[DayResults, errors.UserDoesNotExist]:
    user = (await state.get().users_repo.get_by_id(user_id)).unwrap_or(None)
    if user is None:
        return Err(
            errors.UserDoesNotExist(
                f"User {user} does not exist in the repository, therefore cannot add money"
            )
        )

    income = user.income_today
    expense = user.expense_today
    saved = user.budget_today

    new_remaining_budget = user.remaining_budget + saved
    new_day_budget = new_remaining_budget / (user.days_left - 1) if user.days_left > 1 else user.remaining_budget

    return Ok(
        DayResults(
            income, expense, saved, new_remaining_budget, new_day_budget, user.days_left
        )
    )
