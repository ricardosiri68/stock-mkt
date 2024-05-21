from fastapi import FastAPI, HTTPException, Request, Depends

from typing import Dict
import requests

from stock_mkt.commands import save_users
from stock_mkt.model import SignUpRequest
from stock_mkt.queries import get_current_user, get_stock


app = FastAPI()


@app.post("/signup")
async def signup(request: SignUpRequest):
    users = {}

    if not request.name or not request.last_name or not request.email:
        raise HTTPException(status_code=400, detail="All fields are required")

    api_key = f'api_key_{len(users) + 1}'
    user = request.model_dump()
    user.update({'api_key': api_key}) 
    users[request.email] = user
    save_users(users)

    return {"api_key": api_key}


@app.get("/stock/{symbol}")
async def get_stock(symbol: str, user: dict = Depends(get_current_user)):
    try:
        return get_stock(symbol)
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid symbol or no data available")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
