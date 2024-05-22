from typing import Optional

from stock_mkt.config import MONGO_DB_NAME
from stock_mkt.db import get_db_client
from stock_mkt.model import User, Session
from stock_mkt.cache import get_cache


class UserRepository:

    COLLECTION_NAME = 'users'

    def __init__(self):
        self.__db_client = get_db_client()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.get_collection().find_one({'email': email})

    def save(self, user: User):
        self.get_collection().replace_one({'email': user.email}, user.model_dump())
    
    def get_collection(self):
        return self.__db_client.get_database(MONGO_DB_NAME).get_collection(self.COLLECTION_NAME)


class SessionRepository:

    DB = 0

    def __init__(self):
        self.__cache_client = get_cache(self.DB)

    def save(self, session: Session):
        self.__cache_client.set(session.id, session.user_email, ex=108000)

    def get(self, session_id: str) -> Session:
        user_email = self.__cache_client.get(session_id)
        return Session(id=session_id, user_email=user_email)


class StockRepository:
    pass
