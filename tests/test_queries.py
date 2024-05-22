import json
from unittest import TestCase
import responses

from stock_mkt import queries
from stock_mkt.config import ALPHA_VANTAGE_URL
from stock_mkt.model import Stock
from stock_mkt.cache import get_cache
from stock_mkt.repositories import StockRepository


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
        expected_stock = Stock(
            open='467.1200',
            high='470.7000',
            low='462.2700',
            close='464.6300',
            variation=-4.2099999999999795
        )

        stock = queries.fetch_stock('meta')

        assert stock == expected_stock

    @responses.activate
    def test_fetch_stock_cached(self):
        self.__stub_response()
        expected_stock = Stock(
            open='467.1200',
            high='470.7000',
            low='462.2700',
            close='464.6300',
            variation=-4.2099999999999795
        )

        queries.fetch_stock('meta')
        stock = self.stock_repo.get('meta')

        assert stock == expected_stock


    def __get_response_content(self):
        with open('tests/alpha_response.json', 'r') as f:
            return json.load(f)
    
    def __stub_response(self):
        responses.add(
            'GET',
            ALPHA_VANTAGE_URL,
            json=self.__get_response_content()
        )


class TestCurrentUser(TestCase):


    def test_get_current_user_success(self):
        pass

    def test_get_current_expired_session(self):
        pass

    def test_get_current_session_payload_missmatch(self):
        pass
