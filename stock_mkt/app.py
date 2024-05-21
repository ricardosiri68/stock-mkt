from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict
import requests
import json
import logging

app = FastAPI()

API_KEY = 'X86NOH6II01P7R24'
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'

# Configuración de logging
logging.basicConfig(filename='logs/api.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Cargar usuarios desde el archivo JSON
def load_users():
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Guardar usuarios en el archivo JSON
def save_users(users):
    with open('data/users.json', 'w') as f:
        json.dump(users, f)

users = load_users()


class SignUpRequest(BaseModel):
    name: str
    last_name: str
    email: EmailStr


def get_current_user(api_key: str = Depends(lambda request: request.headers.get('API_KEY'))):
    for user in users.values():
        if user["api_key"] == api_key:
            return user
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/signup")
async def signup(signup_request: SignUpRequest):
    if not signup_request.name or not signup_request.last_name or not signup_request.email:
        raise HTTPException(status_code=400, detail="All fields are required")

    api_key = f'api_key_{len(users) + 1}'
    users[signup_request.email] = {
        'name': signup_request.name,
        'last_name': signup_request.last_name,
        'api_key': api_key
    }
    save_users(users)

    return {"api_key": api_key}


@app.get("/stock/{symbol}")
# async def get_stock(symbol: str, user: dict = Depends(get_current_user)):
async def get_stock(symbol: str):
    response = requests.get(ALPHA_VANTAGE_URL, params={
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'compact',
        'apikey': API_KEY
    })

    data = response.json()

    try:
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

        # Registrar la llamada a la API
        logging.info(f"Stock data retrieved for {symbol}")

        return result

    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid symbol or no data available")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
