from typing import Optional

from stock_mkt.cache import get_cache
from stock_mkt.config import MONGO_DB_NAME, SESSION_TTL, STOCK_TTL
from stock_mkt.db import get_db_client
from stock_mkt.model import Session, Stock, User


class UserRepository:
    """Manage the User object collection."""

    COLLECTION_NAME = 'users'

    def __init__(self):
        """Set the db client."""
        self.__db_client = get_db_client()

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrive a user by the email as the unique key."""
        user = self.get_collection().find_one({'email': email})

        if user:
            return User(**user)

    def save(self, user: User):
        """Storage the user object."""
        self.get_collection().replace_one({'email': user.email}, user.model_dump(), upsert=True)

    def get_collection(self):
        """Select the user mongo db collection."""
        return self.__db_client.get_database(MONGO_DB_NAME).get_collection(self.COLLECTION_NAME)


class CacheRepository:
    """Superclass to implement a memcache repository."""

    NAMESPACE = ''

    def __init__(self):
        """Set the cache client."""
        self.cache_client = get_cache()

    def key(self, key: str) -> str:
        """Add the namespace prefix of the redis key."""
        return f'{self.NAMESPACE}:{key}'


class SessionRepository(CacheRepository):
    """Manage the Session object collection."""

    NAMESPACE = 'sessions'

    def save(self, session: Session):
        """Store the session object in the cache."""
        self.cache_client.set(self.key(session.id), session.user_email, ex=SESSION_TTL)

    def get(self, session_id: str) -> Optional[Session]:
        """Retrive the session object by session id."""
        user_email = self.cache_client.get(self.key(session_id))

        if user_email:
            return Session(id=session_id, user_email=user_email.decode())


class StockRepository(CacheRepository):
    """Manage the Stock object collection."""

    NAMESPACE = 'stock'

    def save(self, symbol: str, stock: Stock):
        """Save the stock object by the symbol key."""
        self.cache_client.set(self.key(symbol), stock.model_dump_json(), ex=STOCK_TTL)

    def get(self, symbol: str) -> Optional[Stock]:
        """Retrive the stock by the symbol key when its cached."""
        stock_data = self.cache_client.get(self.key(symbol))

        if not stock_data:
            return

        return Stock.model_validate_json(stock_data.decode())
