from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    """The request to add a new user to the system."""

    name: str
    last_name: str
    email: EmailStr
    password: str


class LogInRequest(BaseModel):
    """The request to add a new user to the system."""

    email: str
    password: str


class User(BaseModel):
    """The user stored on the database."""

    name: str
    last_name: str
    email: EmailStr
    password: str


class Session(BaseModel):
    """The active session of the user."""

    id: str
    user_email: str


class StockRequest(BaseModel):
    """The request to the backend stock api."""

    function: str
    symbol: str
    outputsize: str
    apikey: str


class StockResponse(BaseModel):
    """The response from the backend stock api."""

    open: str
    high: str
    low: str
    close: str
    variation: float
