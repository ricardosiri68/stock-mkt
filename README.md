# Stock Market API

useful API to query the stock market values of a company

# Installation
After cloning the repository you should copy the `sample.env` to `.env`

Inside the `.env` file you'll find a envvar called `JWT_SECRET`. You must provide your own secret
salt for the jwt algorithm.

Then you need build the proyect with `docker-compose`

```
docker-compose build
```

The you can run up the services:

```
docker-compose up -d
```
A redis and mongo db service will be running as dependencies.

# Test with CRUL

### Sign UP
```bash
curl --request POST \
  --url http://localhost:8080/signup \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/9.2.0' \
  --data '{
	"email": "some@email.com",
	"name": "John",
	"last_name": "Doe",
	"password": "somepwd"
}'
```

### Log In
```bash
curl --request POST \
  --url http://localhost:8080/login \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/9.2.0' \
  --data '{
	"email": "some@email.com",
	"password": "somepwd"
}'
```

Will respond with the api key to use the api like this:

```json
{
	"api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiYmFjNTIyYzAtN2NiMi00YmYxLTgwZGItN2ZlMjk2YWMyOGNjIiwiZW1haWwiOiJzb21lQGVtYWlsLmNvbSJ9.XN5wrB8_mRfDI0E7HSJmJmmUrLwFh1BfoZcy2fa18wY"
}
```

### Get the stock values
You should use the same api kay has header `API_KEY` on the `/stock/{symbol}` in this case will
query the meta stock market value
```bash
curl --request GET \
  --url http://localhost:8080/stock/meta \
  --header 'API_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiYmFjNTIyYzAtN2NiMi00YmYxLTgwZGItN2ZlMjk2YWMyOGNjIiwiZW1haWwiOiJzb21lQGVtYWlsLmNvbSJ9.XN5wrB8_mRfDI0E7HSJmJmmUrLwFh1BfoZcy2fa18wY' \
  --header 'User-Agent: insomnia/9.2.0'
```
The output should look like this:

```json
{
	"open": "467.8700",
	"high": "473.7199",
	"low": "465.6500",
	"close": "467.7800",
	"variation": 3.1499999999999773
}
```

# Running tests

You should run the tests of the proyect with this code very quick

```bash
docker-compose run --entrypoint poetry stock-mkt.app run pytest --cov-report term-missing --cov=stock_mkt -vv tests
```
