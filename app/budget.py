from dataclasses import replace

from app import state
from domain import User
from domain.models.budget import (
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
    user: User, amount: float
) -> Result[Spent | SpentOverDailyBudget | SpentAllBudget, errors.UserDoesNotExist]:
    if not await state.get().users_repo.contains(user):
        return Err(
            errors.UserDoesNotExist(
                f"User {user} does not exist in the repository, therefore cannot spend money"
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
            await state.get().users_repo.remove_user_by_id(user.id)  # FIXME result
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
    user: User, amount: float
) -> Result[Added, errors.UserDoesNotExist]:
    if not await state.get().users_repo.contains(user):
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
    user: User,
) -> Result[DayResults | PeriodEnded, errors.UserDoesNotExist]:
    if not await state.get().users_repo.contains(user):
        return Err(
            errors.UserDoesNotExist(
                f"User {user} does not exist in the repository, therefore cannot be updated"
            )
        )

    income = user.income_today
    expense = user.expense_today
    saved = user.budget_today
    new_days_left = max(user.days_left - 1, 0)

    if new_days_left == 0:
        await state.get().users_repo.remove_user_by_id(user.id)  # FIXME result
        return Ok(PeriodEnded(saved))

    new_remaining_budget = user.remaining_budget + saved
    new_day_budget = new_remaining_budget / new_days_left
    new_remaining_budget -= new_day_budget

    user = replace(
        user,
        income_today=0,
        expense_today=0,
        remaining_budget=new_remaining_budget,
        budget_today=new_day_budget,
    )

    await state.get().users_repo.update_user(user)  # FIXME result

    return Ok(
        DayResults(
            income, expense, saved, new_remaining_budget, new_day_budget, new_days_left
        )
    )
