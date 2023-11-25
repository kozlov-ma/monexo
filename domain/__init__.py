from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from domain.models.budget import BudgetChange, IncorrectTransaction


__user_repository = UserRepository()


def user_repository() -> UserRepository:
    return __user_repository
