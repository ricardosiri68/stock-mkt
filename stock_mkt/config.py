import os

API_KEY = os.environ.get('API_KEY')
ALPHA_VANTAGE_URL = os.environ.get('ALPHA_VANTAGE_URL')
REDIS_DB_URI = os.environ.get('REDIS_DB_URI')
SESSION_TTL = int(os.environ.get('SESSION_TTL', 0))
STOCK_TTL = int(os.environ.get('STOCK_TTL', 0))
MONGO_DB_URI = os.environ.get('MONGO_DB_URI')
MONGO_DB_NAME = 'stock_mkt'
JWT_SECRET = os.environ.get('JWT_SECRET')
