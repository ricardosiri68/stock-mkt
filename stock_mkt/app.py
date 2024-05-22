from http import HTTPStatus
from typing import Dict
import json

import requests
from fastapi import FastAPI, HTTPException, Request, Depends, Response

from stock_mkt.commands import login_user, signup_user
from stock_mkt.model import LogInRequest, SignUpRequest
from stock_mkt.queries import fetch_stock, get_current_user



app = FastAPI()


@app.post("/signup")
async def signup(request: SignUpRequest):
    signup_user(request)
    return Response(status_code=HTTPStatus.NO_CONTENT)


@app.post("/login")
async def login(request: LogInRequest):
    api_key = login_user(request.email, request.password)
    return Response(status_code=HTTPStatus.CREATED, content=json.dumps({'api_key': api_key}))


@app.get("/stock/{symbol}")
async def get_stock(request: Request, symbol: str):
    get_current_user(request)
    try:
        return fetch_stock(symbol)
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid symbol or no data available")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
