from http import HTTPStatus
from uuid import uuid4

from fastapi import HTTPException

from stock_mkt.crypto_utils import JwtManager, hash_password
from stock_mkt.model import Session, User
from stock_mkt.repositories import SessionRepository, UserRepository


def signup_user(signup: User):
    """Sign Up a new user and store his data profile."""
    repo = UserRepository()
    user = repo.get_by_email(signup.email)

    if user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User already exists !!'
        )

    user = User(
        email=signup.email,
        name=signup.name,
        last_name=signup.last_name,
        password=hash_password(signup.password)
    )
    repo.save(user)


def login_user(email: str, password: str):
    """Sign log in a registered user and store the session on cache."""
    jwt_manager = JwtManager()
    user_repo = UserRepository()
    session_repo = SessionRepository()
    user = user_repo.get_by_email(email)

    if not user or user.password != hash_password(password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid login !!'
        )

    session_id = str(uuid4())
    session_repo.save(Session(id=session_id, user_email=user.email))

    return jwt_manager.encode({'session_id': session_id, 'email': user.email})
