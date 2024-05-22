from typing import Optional

from stock_mkt.config import MONGO_DB_NAME, SESSION_TTL, STOCK_TTL
from stock_mkt.db import get_db_client
from stock_mkt.model import User, Session, Stock
from stock_mkt.cache import get_cache


class UserRepository:

    COLLECTION_NAME = 'users'

    def __init__(self):
        self.__db_client = get_db_client()
    
    def get_by_email(self, email: str) -> Optional[User]:
        user = self.get_collection().find_one({'email': email})

        if user:
            return User(**user)

    def save(self, user: User):
        self.get_collection().replace_one({'email': user.email}, user.model_dump(), upsert=True)
    
    def get_collection(self):
        return self.__db_client.get_database(MONGO_DB_NAME).get_collection(self.COLLECTION_NAME)


class CacheRepository:

    NAMESPACE = ''

    def __init__(self):
        self.cache_client = get_cache()

    def key(self, key: str) -> str:
        return f'{self.NAMESPACE}:{key}'


class SessionRepository(CacheRepository):

    NAMESPACE = 'sessions'

    def save(self, session: Session):
        self.cache_client.set(self.key(session.id), session.user_email, ex=SESSION_TTL)

    def get(self, session_id: str) -> Optional[Session]:
        user_email = self.cache_client.get(self.key(session_id))

        if user_email:
            return Session(id=session_id, user_email=user_email.decode())


class StockRepository(CacheRepository):

    NAMESPACE = 'stock'

    def save(self, symbol: str, stock: Stock):
        self.cache_client.set(self.key(symbol), stock.model_dump_json(), ex=STOCK_TTL)

    def get(self, symbol: str) -> Optional[Stock]:
        stock_data = self.cache_client.get(self.key(symbol))

        if not stock_data:
            return

        return Stock.model_validate_json(stock_data.decode())
