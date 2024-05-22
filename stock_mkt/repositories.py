from typing import Optional

from stock_mkt.config import MONGO_DB_NAME, SESSION_TTL
from stock_mkt.db import get_db_client
from stock_mkt.model import User, Session
from stock_mkt.cache import get_cache


class UserRepository:

    COLLECTION_NAME = 'users'

    def __init__(self):
        self.__db_client = get_db_client()
    
    def get_by_email(self, email: str) -> Optional[User]:
        user = self.get_collection().find_one({'email': email})
        return User(**user)

    def save(self, user: User):
        self.get_collection().replace_one({'email': user.email}, user.model_dump(), upsert=True)
    
    def get_collection(self):
        return self.__db_client.get_database(MONGO_DB_NAME).get_collection(self.COLLECTION_NAME)


class SessionRepository:

    NAMESPACE = 'sessions'

    def __init__(self):
        self.__cache_client = get_cache()

    def save(self, session: Session):
        self.__cache_client.set(self.key(session.id), session.user_email, ex=SESSION_TTL)

    def get(self, session_id: str) -> Session:
        user_email = self.__cache_client.get(self.key(session_id))
        return Session(id=session_id, user_email=user_email.decode())
    
    def key(self, session_id: str) -> str:
        return f'{self.NAMESPACE}:{session_id}'


class StockRepository:
    pass
