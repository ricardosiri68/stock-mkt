import hashlib

import jwt

from stock_mkt.config import JWT_SECRET


def hash_password(plaintext: str):
    """Make a unidirectional hash with the plain text password of the user."""
    hash_object = hashlib.sha256()
    hash_object.update(plaintext.encode())
    return hash_object.hexdigest()


class JwtManager:
    """Provide a facade to a encode/decode api keys a jwt algorithm."""

    ALGORITHM = 'HS256'

    def __init__(self):
        """Initialize the secret."""
        self.__secret = JWT_SECRET

    def encode(self, payload: dict) -> str:
        """Encode the payload into a jwt."""
        return jwt.encode(payload, self.__secret, self.ALGORITHM)

    def decode(self, encrypted_text: str) -> dict:
        """Decode the jwt token back to the original payload."""
        return jwt.decode(encrypted_text, self.__secret, algorithms=[self.ALGORITHM])
