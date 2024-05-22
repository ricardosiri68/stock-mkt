from http import HTTPStatus
from uuid import uuid4, UUID

from stock_mkt.crypto_utils import JwtManager, hash_password
from stock_mkt.model import Session, User
from stock_mkt.repositories import SessionRepository, UserRepository


def signup_user(signup: User):

    if not signup.name or not signup.last_name or not signup.email:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="All fields are required")

    repo = UserRepository()
    user = repo.get_by_email(signup.email)

    if user:
        raise Exception('User already exists !!')

    user = User(
        email=signup.email,
        name=signup.name,
        last_name=signup.last_name,
        password=hash_password(signup.password)
    )
    repo.save(user)


def login_user(email: str, password: str):
    jwt_manager = JwtManager()
    user_repo = UserRepository()
    session_repo = SessionRepository()
    user = user_repo.get_by_email(email)

    if user.password != hash_password(password):
        raise Exception('Invalid login !!')

    session_id = str(uuid4())
    session_repo.save(Session(id=session_id, user_email=user.email))

    return jwt_manager.encode({'session_id': session_id, 'email': user.email})
