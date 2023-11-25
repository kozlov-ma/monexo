from app import state
from domain import BudgetChange, User
from domain.models.budget import Spent, Added, SpentOverDailyBudget
from option import Result, Ok, Err
from app import errors


async def add_expense(
    user: User, amount: float
) -> Result[Spent, errors.UserDoesNotExist]:
    user = user.add_expense(amount)
    await state.get().users_repo.update_user(user)  # FIXME Result

    return Ok(Spent(amount))
