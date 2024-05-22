from redis import Redis

from stock_mkt.config import REDIS_DB_URI


def get_cache(db=0):
    return Redis.from_url(url=REDIS_DB_URI, db=db)
