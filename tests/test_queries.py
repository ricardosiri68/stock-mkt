from http import HTTPStatus
from unittest import TestCase

from fastapi import HTTPException
import pytest
import responses

from stock_mkt import queries
from stock_mkt.cache import get_cache
from stock_mkt.commands import login_user
from stock_mkt.crypto_utils import hash_password
from stock_mkt.model import Stock, User
from stock_mkt.repositories import StockRepository, UserRepository
from tests.utils import clear_cache, clear_users, stub_response


class TestFetchStock(TestCase):
    
    def setUp(self):
        super().setUp()
        self.stock_repo = StockRepository()

    def tearDown(self):
        """Clear the cache."""
        super().tearDown()
        clear_cache()

    @responses.activate
    def test_fetch_stock_success(self):
        stub_response()
        expected_stock = self.__expected_stock()

        stock = queries.fetch_stock('meta')

        assert stock == expected_stock

    @responses.activate
    def test_fetched_stock_is_stored_on_cache(self):
        stub_response()
        expected_stock = self.__expected_stock()

        queries.fetch_stock('meta')
        stock = self.stock_repo.get('meta')

        assert stock == expected_stock

    def test_fetch_stock_cached(self):
        expected_stock = self.__expected_stock()
        self.stock_repo.save('meta', expected_stock)

        stock = queries.fetch_stock('meta')

        assert stock == expected_stock

    def __expected_stock(self):
        return Stock(
            open='467.1200',
            high='470.7000',
            low='462.2700',
            close='464.6300',
            variation=-4.2099999999999795
        )


class TestCurrentUser(TestCase):

    def setUp(self):
        super().setUp()
        self.cache = get_cache()
        self.user_repo = UserRepository()
        self.user = User(
            email='some@email.com',
            name='Some',
            last_name='Lastname',
            password=hash_password('somepass')
        )
        self.user_repo.save(self.user)
        self.api_key = login_user(self.user.email, 'somepass')

    def tearDown(self):
        """Clear the cache."""
        super().tearDown()
        clear_cache()
        clear_users()

    def test_get_current_user_success(self):
        result = queries.get_current_user(self.api_key)
        assert result is None

    def test_get_current_expired_session(self):
        self.cache.flushall()
        with pytest.raises(HTTPException) as error:
            queries.get_current_user(self.api_key)
            assert error.status_code == HTTPStatus.UNAUTHORIZED
