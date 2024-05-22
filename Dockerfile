FROM python:3.10

WORKDIR /app
COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
COPY .flake8 /app/.flake8
RUN pip install poetry && poetry install

RUN mkdir /data /app/logs
RUN touch /app/logs/api.log
RUN touch /data/users.json
COPY stock_mkt /app/stock_mkt
COPY tests /app/tests
COPY scripts /app/scripts
RUN chmod -R +x /app/scripts
