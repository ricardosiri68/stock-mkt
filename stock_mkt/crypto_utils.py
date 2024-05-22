import hashlib
import jwt

from stock_mkt.config import JWT_SECRET


def hash_password(plaintext: str):
    hash_object = hashlib.sha256()
    hash_object.update(plaintext.encode())
    return hash_object.hexdigest()


class JwtManager:

    ALGORITM = 'HS256'

    def __init__(self):
        self.__secret = JWT_SECRET

    def encode(self, payload: dict) -> str:
        return jwt.encode(payload, self.__secret, self.ALGORITM)

    def decode(self, jwt: str) -> dict:
        return jwt.decode(jwt, self.__secret, algorithms=[self.ALGORITM])
