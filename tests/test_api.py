import json
from unittest import TestCase
from http import HTTPStatus

from fastapi.testclient import TestClient
import responses

from stock_mkt.app import app
from stock_mkt.repositories import UserRepository
from stock_mkt.db import get_db_client
from stock_mkt.config import MONGO_DB_NAME, ALPHA_VANTAGE_URL
from stock_mkt.crypto_utils import hash_password
from stock_mkt.model import User
from stock_mkt.cache import get_cache
from stock_mkt.commands import login_user

client = TestClient(app)


class TestSignUpEndpoint(TestCase):

    def tearDown(self):
        super().tearDown()
        db_client = get_db_client()
        db_client.get_database(MONGO_DB_NAME).drop_collection(UserRepository.COLLECTION_NAME)

    def test_signup_success(self):
        user_json = {
            'email': 'some@email.com',
            'name': 'Some',
            'last_name': 'Lastname',
            'password': 'somepwd'
        }
        response = client.post('/signup', json=user_json)

        assert response.status_code == HTTPStatus.CREATED

    def test_signup_unprocessable_entity(self):
        user_json = {
            'email': 'some@email.com',
            'ssword': 'somepwd'
        }
        response = client.post('/signup', json=user_json)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestLoginEndpoint(TestCase):

    def setUp(self):
        self.user_repo = UserRepository()
        self.user = User(
            email='some@email.com',
            name='Some',
            last_name='Lastname',
            password=hash_password('somepass')
        )
        self.user_repo.save(self.user)

    def tearDown(self):
        super().tearDown()
        db_client = get_db_client()
        db_client.get_database(MONGO_DB_NAME).drop_collection(UserRepository.COLLECTION_NAME)
        cache = get_cache()
        cache.flushall()
        
    def test_login_success(self):
        response = client.post('/login', json={'email': 'some@email.com', 'password': 'somepass'})

        assert response.status_code == HTTPStatus.NO_CONTENT
        
    def test_login_content(self):
        response = client.post('/login', json={'email': 'some@email.com', 'password': 'somepass'})

        assert 'api_key' in response.json().keys()

    def test_unprocessable_entity(self):
        response = client.post('/login', json={'badfield': 'badvalue', 'password': 'somepass'})

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestGetStockEndpoint(TestCase):

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

    @responses.activate
    def test_get_stock_success(self):
        self.__stub_response()
        expected_response = {
            'status': HTTPStatus.OK,
            'content': {
                'close': '464.6300',
                'high': '470.7000',
                'low': '462.2700',
                'open': '467.1200',
                'variation': -4.2099999999999795
            }
        }
        response = client.get('/stock/meta', headers={'API_KEY': self.api_key})
        response = {
            'status': response.status_code,
            'content': response.json()
        }

        assert response == expected_response

    def test_get_stock_unauthorized(self):
        wrong_api_key = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                         '.eyJzZXNzaW9uX2lkIjoiOGQ4NmE0NWUtYTliZS00NzNm'
                         'LTllODYtZGUyMTY0ODQ3Yzk5IiwiZW1haWwiOiJzb21lQGVtYWlsLmNvbSJ9'
                         '.tt1ixl_wcjg_VEhfN_1v8vWWPHky14NugGKTtYsHvoA')
        response = client.get('/stock/meta', headers={'API_KEY': wrong_api_key})

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @responses.activate
    def test_get_unknown_symbol(self):
        responses.add(
            'GET',
            ALPHA_VANTAGE_URL,
            json=self.__get_wrong_symbol_content()
        )
        response = client.get('/stock/zeta', headers={'API_KEY': self.api_key})

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def __get_response_content(self):
        with open('tests/responses/alpha_response.json', 'r') as f:
            return json.load(f)

    def __get_wrong_symbol_content(self):
        with open('tests/responses/wrong_symbol_response.json', 'r') as f:
            return json.load(f)
    
    def __stub_response(self):
        responses.add(
            'GET',
            ALPHA_VANTAGE_URL,
            json=self.__get_response_content()
        )
