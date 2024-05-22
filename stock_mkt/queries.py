import json

from fastapi import HTTPException, Depends

from stock_mkt import config
from stock_mkt.model import StockRequest, StockResponse
from stock_mkt.logs import logging
from stock_mkt.repositories import UserRepository, SessionRepository
from stock_mkt.crypto_utils import JwtManager


def get_stock(symbol: str):
    request = StockRequest(
        function='TIME_SERIES_DAILY',
        symbol=symbol,
        outputsize='compact',
        apikey=config.API_KEY
    )
    response = requests.get(config.ALPHA_VANTAGE_URL, params=request)
    data = response.json()

    time_series = data['Time Series (Daily)']
    dates = sorted(time_series.keys(), reverse=True)
    latest = time_series[dates[0]]
    previous = time_series[dates[1]]

    result = {
        'open': latest['1. open'],
        'high': latest['2. high'],
        'low': latest['3. low'],
        'close': latest['4. close'],
        'variation': float(latest['4. close']) - float(previous['4. close'])
    }

    logging.info(f"Stock data retrieved for {symbol}")

    return StockResponse(**data)


def get_current_user(api_key: str = Depends(lambda request: request.headers.get('API_KEY'))):
    jwt_manager = JwtManager()()
    session_repo = SessionRepository()
    session_data = jwt_manager.decode(api_key)

    session = Session(session_data.get('session_id'), session_data.get('user_email'))
    user_email = session_repo.get(session.id)

    if not user_email:
        raise HTTPException(status_code=401, detail="Unauthorized")
