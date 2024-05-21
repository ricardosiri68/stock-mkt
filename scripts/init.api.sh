#!/usr/bin/env bash

poetry run uvicorn stock_mkt.app:app --reload --host 0.0.0.0 --port 80
