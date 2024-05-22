from pymongo import MongoClient

from stock_mkt.config import MONGO_DB_URI


def get_db_client():

    return MongoClient(MONGO_DB_URI)
