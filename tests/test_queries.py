import json
from http import HTTPStatus
from unittest import TestCase

import responses
import pytest
from fastapi import Request, HTTPException

from stock_mkt import queries
from stock_mkt.cache import get_cache
from stock_mkt.config import ALPHA_VANTAGE_URL, MONGO_DB_NAME
from stock_mkt.commands import login_user
from stock_mkt.crypto_utils import hash_password
from stock_mkt.db import get_db_client
from stock_mkt.model import Stock, User
from stock_mkt.repositories import StockRepository, UserRepository


class TestFetchStock(TestCase):
    
    def setUp(self):
        super().setUp()
        self.stock_repo = StockRepository()

    def tearDown(self):
        """Clear the cache."""
        super().tearDown()
        cache = get_cache()
        cache.flushall()

    @responses.activate
    def test_fetch_stock_success(self):
        self.__stub_response()
        expected_stock = self.__expected_stock()

        stock = queries.fetch_stock('meta')

        assert stock == expected_stock

    @responses.activate
    def test_fetched_stock_is_stored_on_cache(self):
        self.__stub_response()
        expected_stock = self.__expected_stock()

        queries.fetch_stock('meta')
        stock = self.stock_repo.get('meta')

        assert stock == expected_stock

    def test_fetch_stock_cached(self):
        expected_stock = self.__expected_stock()
        self.stock_repo.save('meta', expected_stock)

        stock = queries.fetch_stock('meta')

        assert stock == expected_stock


    def __get_response_content(self):
        with open('tests/responses/alpha_response.json', 'r') as f:
            return json.load(f)
    
    def __stub_response(self):
        responses.add(
            'GET',
            ALPHA_VANTAGE_URL,
            json=self.__get_response_content()
        )

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
        self.__db_client = get_db_client()
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
        self.cache.flushall()
        self.__db_client.get_database(MONGO_DB_NAME).drop_collection(UserRepository.COLLECTION_NAME)

    def test_get_current_user_success(self):
        result = queries.get_current_user(self.api_key)
        assert result is None

    def test_get_current_expired_session(self):
        self.cache.flushall()
        with pytest.raises(HTTPException) as error:
            queries.get_current_user(self.api_key)
            assert error.status_code == HTTPStatus.UNAUTHORIZED
