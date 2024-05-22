import json

from fastapi import HTTPException, Request
import requests

from stock_mkt import config
from stock_mkt.model import StockRequest, Stock, Session
from stock_mkt.logs import logging
from stock_mkt.repositories import UserRepository, SessionRepository, StockRepository
from stock_mkt.crypto_utils import JwtManager


def fetch_stock(symbol: str):
    stock_repo = StockRepository()
    stock = stock_repo.get(symbol)

    if stock:
        return stock

    request = StockRequest(
        function='TIME_SERIES_DAILY',
        symbol=symbol,
        outputsize='compact',
        apikey=config.API_KEY
    )
    response = requests.get(config.ALPHA_VANTAGE_URL, params=request.model_dump())
    data = response.json()

    time_series = data['Time Series (Daily)']
    dates = sorted(time_series.keys(), reverse=True)
    latest = time_series[dates[0]]
    previous = time_series[dates[1]]

    logging.info(f"Stock data retrieved for {symbol}")

    stock = Stock(
        open=latest.get('1. open'),
        high=latest.get('2. high'),
        low=latest.get('3. low'),
        close=latest.get('4. close'),
        variation=float(latest.get('4. close')) - float(previous.get('4. close'))
    )
    stock_repo.save(symbol, stock)

    return stock


def get_current_user(request: Request):
    api_key = request.headers.get('API_KEY')
    jwt_manager = JwtManager()
    session_repo = SessionRepository()
    session_data = jwt_manager.decode(api_key)
    session = session_repo.get(session_data.get('session_id'))

    if session and session_data.get('email') != session.user_email:
        raise HTTPException(status_code=401, detail="Unauthorized")
