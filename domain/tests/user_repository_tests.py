from unittest import IsolatedAsyncioTestCase
from domain.models.user import User
from domain.repositories.user_repository import UserRepository


class UserRepositoryTests(IsolatedAsyncioTestCase):
    async def test_get_all(self):
        repository: UserRepository = UserRepository()

        user1: User = User(
            id=0,
            days_left=999,
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        user2: User = User(
            id=1,
            days_left=999,
            whole_budget=222,
            expense_today=22,
            income_today=2,
        )

        add_user_result_1 = await repository.add_user(user1)
        add_user_result_2 = await repository.add_user(user2)

        result_users = await repository.get_all()

        self.assertTrue(add_user_result_1.is_ok)
        self.assertTrue(add_user_result_2.is_ok)
        self.assertTrue(result_users.is_ok)
        self.assertEqual(len(result_users.ok().value), 2)
        self.assertIn(user1, result_users.ok().value)
        self.assertIn(user2, result_users.ok().value)

    async def test_get_by_id(self):
        repository = UserRepository()

        user: User = User(
            id=0,
            days_left=999,
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        add_user_result = await repository.add_user(user)

        found_user_result = await repository.get_by_id(user.id)

        self.assertTrue(add_user_result.is_ok)
        self.assertTrue(found_user_result.is_ok)
        self.assertEqual(user, found_user_result.ok().value)

    async def test_remove_user_by_id(self):
        repository = UserRepository()

        user: User = User(
            id=0,
            days_left=999,
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        add_user_result = await repository.add_user(user)
        remove_user_result = await repository.remove_user_by_id(user.id)

        users_result = await repository.get_all()

        self.assertTrue(add_user_result.is_ok)
        self.assertTrue(remove_user_result.is_ok)
        self.assertTrue(users_result.is_ok)
        self.assertNotIn(user, users_result.ok().value)

    async def test_update_user(self):
        repository = UserRepository()

        user: User = User(
            id=0,
            days_left=999,
            whole_budget=111,
            expense_today=11,
            income_today=1,
        )

        add_user_result = await repository.add_user(user)

        updated_user: User = User(
            id=user.id,
            days_left=999,
            whole_budget=333,
            expense_today=33,
            income_today=3,
        )

        update_user_result = await repository.update_user(updated_user)

        find_user_result = await repository.get_by_id(user.id)

        self.assertTrue(add_user_result.is_ok)
        self.assertTrue(update_user_result.is_ok)
        self.assertTrue(find_user_result.is_ok)
        self.assertEqual(find_user_result.ok().value, updated_user)
