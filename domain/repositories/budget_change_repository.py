from abc import ABC, abstractmethod
from dataclasses import replace
from option import Option, Result, Ok, Err

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.category import Category, DbCategory
from domain.models.budget_change import BudgetChange, DbBudgetChange


class BudgetChangeRepositoryBase(ABC):
    def __init__(self, session: AsyncSession | None = None) -> None:
        pass

    @abstractmethod
    async def get_all_categories(self) -> list[Category]:
        pass

    @abstractmethod
    async def get_categories_by_telegram_id(self, telegram_id: int) -> Option[list[Category]]:
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> Option[Category]:
        pass

    @abstractmethod
    async def add_category(self, category: Category) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def remove_category_by_id(self, category_id: int) -> Option[Category]:
        pass

    @abstractmethod
    async def get_all_budget_changes(self) -> list[BudgetChange]:
        pass

    @abstractmethod
    async def get_budget_changes_by_telegram_id(self, telegram_id: int, category_id: int = None
                                                ) -> list[BudgetChange]:
        pass

    @abstractmethod
    async def get_budget_changes_by_message_id(self, message_id: int) -> Option[BudgetChange]:
        pass

    @abstractmethod
    async def add_budget_change(self, budget_change: BudgetChange) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def remove_budget_change_by_id(self, budget_change_id: int) -> Option[BudgetChange]:
        pass

    @abstractmethod
    async def remove_all_budget_changes_by_tg_id(self, telegram_id: int) -> Option[list[BudgetChange]]:
        pass


class PostgresBudgetChangeRepository(BudgetChangeRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session: AsyncSession = session

    async def get_all_categories(self) -> list[Category]:
        statement = select(DbCategory)
        return list(category.to_category() for category in await self.session.scalars(statement))

    async def get_categories_by_telegram_id(self, telegram_id: int) -> Option[list[Category]]:
        statement = (select(DbCategory)
                     .where(DbCategory.user_telegram_id == telegram_id))

        categories = await self.session.scalars(statement)

        if categories is None:
            return Option.NONE()

        return Option.Some(list(category.to_category() for category in categories))

    async def get_category_by_id(self, category_id: int) -> Option[Category]:
        statement = (select(DbCategory)
                     .where(DbCategory.id == category_id))

        category = await self.session.scalar(statement)

        if category is None:
            return Option.NONE()

        return Option.Some(category.to_category())

    async def add_category(self, category: Category) -> Result[None, Exception]:
        statement = (select(DbCategory)
                     .where(DbCategory.id == category.id))

        get_category = await self.session.scalar(statement)

        if get_category is not None:
            return Err(KeyError(f"User with id {category.id} already exists"))

        self.session.add(DbCategory.from_category(category))
        await self.session.commit()
        return Ok(None)

    async def remove_category_by_id(self, category_id: int) -> Option[Category]:
        statement = (select(DbCategory)
                     .where(DbCategory.id == category_id))

        get_category = await self.session.scalar(statement)

        if get_category is None:
            return Option.NONE()

        await self.session.delete(get_category)
        await self.session.commit()

        return Option.Some(get_category.to_category())

    async def get_all_budget_changes(self) -> list[BudgetChange]:
        statement = select(DbBudgetChange)
        return list(budget_change.to_budget_change() for budget_change in await self.session.scalars(statement))

    async def get_budget_changes_by_telegram_id(self, telegram_id: int, category_id: int = None
                                                ) -> list[BudgetChange]:
        if category_id is None:
            statement = (select(DbBudgetChange)
                         .where(DbBudgetChange.user_telegram_id == telegram_id))
        else:
            statement = (select(DbBudgetChange)
                         .where(and_(DbBudgetChange.user_telegram_id == telegram_id,
                                     DbBudgetChange.category_id == category_id)))

        budget_changes = await self.session.scalars(statement)

        if budget_changes is None:
            return []

        return list(budget_change.to_budget_change() for budget_change in budget_changes)

    async def get_budget_changes_by_message_id(self, message_id: int) -> Option[BudgetChange]:
        statement = (select(DbBudgetChange)
                     .where(DbBudgetChange.message_telegram_id == message_id))

        budget_change = await self.session.scalar(statement)

        if budget_change is None:
            return Option.NONE()

        return Option.Some(budget_change.to_budget_change())

    async def add_budget_change(self, budget_change: BudgetChange) -> Result[None, Exception]:
        statement = (select(DbBudgetChange)
                     .where(DbBudgetChange.id == budget_change.id))

        get_budget_change = await self.session.scalar(statement)

        if get_budget_change is not None:
            return Err(KeyError(f"User with id {budget_change.id} already exists"))

        self.session.add(DbBudgetChange.from_budget_change(budget_change))
        await self.session.commit()
        return Ok(None)

    async def remove_budget_change_by_id(self, budget_change_id: int) -> Option[BudgetChange]:
        statement = (select(DbBudgetChange)
                     .where(DbBudgetChange.id == budget_change_id))

        get_budget_change = await self.session.scalar(statement)

        if get_budget_change is None:
            return Option.NONE()

        await self.session.delete(get_budget_change)
        await self.session.commit()

        return Option.Some(get_budget_change.to_budget_change())

    async def remove_all_budget_changes_by_tg_id(self, telegram_id: int) -> list[BudgetChange]:
        budget_changes = []
        for c in (await self.get_categories_by_telegram_id(telegram_id)).unwrap_or([]) + [None]:
            changes = await self.get_budget_changes_by_telegram_id(telegram_id)
            for change in changes:
                bc = await self.remove_budget_change_by_id(change.id)
                if bc.is_some:
                    budget_changes.append(bc.unwrap())
        return budget_changes


BudgetChangeRepository: type = PostgresBudgetChangeRepository
