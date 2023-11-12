from unittest import IsolatedAsyncioTestCase
from uuid import uuid4
from datetime import date
from domain.models.user import User
from domain.repositories.user_repository import UserRepository


class UserRepositoryTests(IsolatedAsyncioTestCase):
    async def test_get_all(self):
        repository: UserRepository = UserRepository()

        user1: User = User(
            id=uuid4(),
            telegram_id="user1",
            period=date(2031, 12, 31),
            whole_budget=100,
            expense=10,
            income=1,
        )

        user2: User = User(
            id=uuid4(),
            telegram_id="user2",
            period=date(2042, 11, 10),
            whole_budget=100000,
            expense=1000,
            income=1052,
        )

        await repository.add_user(user1)
        await repository.add_user(user2)

        users: list[User] = await repository.get_all()

        self.assertEqual(len(users), 2)
        self.assertIn(user1, users)
        self.assertIn(user2, users)

    async def test_get_by_id(self):
        repository = UserRepository()

        user = User(
            id=uuid4(),
            telegram_id="user",
            period=date(5743, 1, 3),
            whole_budget=7465,
            expense=561,
            income=0,
        )

        await repository.add_user(user)

        found_user = await repository.get_by_id(user.id)

        self.assertEqual(user, found_user)

    async def test_get_by_telegram_id(self):
        repository = UserRepository()

        user = User(
            id=uuid4(),
            telegram_id="user",
            period=date(2401, 2, 7),
            whole_budget=100,
            expense=10,
            income=0,
        )

        await repository.add_user(user)

        found_user = await repository.get_by_telegram_id(user.telegram_id)

        self.assertEqual(user, found_user)

    async def test_remove_user_by_id(self):
        repository = UserRepository()

        user = User(
            id=uuid4(),
            telegram_id="user",
            period=date(2401, 2, 7),
            whole_budget=100,
            expense=10,
            income=0,
        )

        await repository.add_user(user)
        await repository.remove_user_by_id(user.id)

        users = await repository.get_all()

        self.assertNotIn(user, users)

    async def test_update_user(self):
        repository = UserRepository()

        user = User(
            id=uuid4(),
            telegram_id="user",
            period=date(2401, 2, 7),
            whole_budget=100,
            expense=10,
            income=0,
        )

        await repository.add_user(user)

        updated_user = User(
            id=user.id,
            telegram_id="updated_user",
            period=date(2402, 3, 8),
            whole_budget=101,
            expense=11,
            income=1,
        )

        await repository.update_user(updated_user)

        found_user = await repository.get_by_id(user.id)

        self.assertEqual(found_user, updated_user)
