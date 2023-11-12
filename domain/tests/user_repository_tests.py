from unittest import IsolatedAsyncioTestCase
from datetime import date
from domain.models.user import User
from domain.repositories.user_repository import UserRepository


class UserRepositoryTests(IsolatedAsyncioTestCase):
    async def test_get_all(self):
        repository: UserRepository = UserRepository()

        user1: User = User(
            id=0,
            period=date(2111, 11, 11),
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        user2: User = User(
            id=1,
            period=date(2222, 12, 22),
            whole_budget=222,
            expense_today=22,
            income_today=2,
        )

        await repository.add_user(user1)
        await repository.add_user(user2)

        users: list[User] = await repository.get_all()

        self.assertEqual(len(users), 2)
        self.assertIn(user1, users)
        self.assertIn(user2, users)

    async def test_get_by_id(self):
        repository = UserRepository()

        user: User = User(
            id=0,
            period=date(2111, 11, 11),
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        await repository.add_user(user)

        found_user = await repository.get_by_id(user.id)

        self.assertEqual(user, found_user)

    async def test_remove_user_by_id(self):
        repository = UserRepository()

        user: User = User(
            id=0,
            period=date(2111, 11, 11),
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        await repository.add_user(user)
        await repository.remove_user_by_id(user.id)

        users = await repository.get_all()

        self.assertNotIn(user, users)

    async def test_update_user(self):
        repository = UserRepository()

        user: User = User(
            id=0,
            period=date(2111, 11, 11),
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        await repository.add_user(user)

        updated_user: User = User(
            id=user.id,
            period=date(2111, 11, 11),
            whole_budget=333,
            expense_today=33,
            income_today=3,
        )

        await repository.update_user(updated_user)

        found_user = await repository.get_by_id(user.id)

        self.assertEqual(found_user, updated_user)
