import json

import responses

from stock_mkt.cache import get_cache
from stock_mkt.config import ALPHA_VANTAGE_URL, MONGO_DB_NAME
from stock_mkt.db import get_db_client
from stock_mkt.repositories import UserRepository


def response_content(content_name: str) -> dict:
    with open(f'tests/responses/{content_name}.json', 'r') as f:
        return json.load(f)


def stub_response():
    responses.add(
        'GET',
        ALPHA_VANTAGE_URL,
        json=response_content('alpha_response')
    )


def clear_cache():
    cache = get_cache()
    cache.flushall()


def clear_users():
    db_client = get_db_client()
    db_client.get_database(MONGO_DB_NAME).drop_collection(UserRepository.COLLECTION_NAME)
