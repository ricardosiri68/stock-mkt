from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    """The request to add a new user to the system."""

    name: str
    last_name: str
    email: EmailStr


class StockRequest(BaseModel):
    """The request to the backend stock api."""

    function: str
    symbol: str
    outputsize: str


class StockResponse(BaseModel):
    """The response from the backend stock api."""

    open: str
    high: str
    low: str
    close: str
    variation: float
