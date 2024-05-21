import json

from fastapi import HTTPException, Depends

from stock_mkt import config
from stock_mkt.model import StockRequest, StockResponse
from stock_mkt.logs import logging


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


def load_users():
    try:
        with open('/data/users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


users = load_users()


def get_current_user(api_key: str = Depends(lambda request: request.headers.get('API_KEY'))):
    for user in users.values():
        if user["api_key"] == api_key:
            return user

    raise HTTPException(status_code=401, detail="Unauthorized")
