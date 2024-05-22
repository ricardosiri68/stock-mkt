from redis import Redis

from stock_mkt.config import REDIS_DB_URI


def get_cache():
    return Redis.from_url(url=REDIS_DB_URI)
