from unittest import TestCase

import pytest

from stock_mkt import commands
from stock_mkt.crypto_utils import hash_password, JwtManager
from stock_mkt.model import User
from stock_mkt.repositories import UserRepository
from tests.utils import clear_users


class TestSignup(TestCase):

    def setUp(self):
        self.user_repo = UserRepository()

    def tearDown(self):
        super().tearDown()
        clear_users()

    def test_signup_success(self):
        expected_user = self.__user_entity()
        commands.signup_user(expected_user)
        user = self.user_repo.get_by_email(expected_user.email)

        assert user.email == expected_user.email

    def test_signup_fail_by_duplicated_email(self):
        previous_user = self.__user_entity()
        self.user_repo.save(previous_user)

        with pytest.raises(Exception) as error:
            commands.signup_user(previous_user)
            assert str(error) == 'User already exists !!'

    def __user_entity(self):
        return User(
            email='some@email.com',
            name='Some',
            last_name='Somelastname',
            password='some'
        )



class TestLogin(TestCase):

    def setUp(self):
        self.jwt_manager = JwtManager()
        self.user_repo = UserRepository()
        self.user = User(
            email='some@email.com',
            name='Some',
            last_name='Somelastname',
            password=hash_password('some')
        )
        self.user_repo.save(self.user)

    def tearDown(self):
        super().tearDown()
        clear_users()

    def test_login_success(self):
        api_key = commands.login_user('some@email.com', 'some')

        payload = self.jwt_manager.decode(api_key)

        assert payload.get('email') == 'some@email.com'

    def test_login_fail_user_dont_exists(self):
        with pytest.raises(Exception) as error:
            commands.login_user('no_one@email.com', 'noone')
            assert str(error) == 'Invalid login !!'

    def test_login_fail_wrong_password(self):
        with pytest.raises(Exception) as error:
            commands.login_user('some@email.com', 'somee')
            assert str(error) == 'Invalid login !!'
