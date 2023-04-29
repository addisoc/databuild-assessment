#!/bin/sh

export APP_MODULE=${APP_MODULE-src.app.main:app}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8080}


# The program is run with the following command:
exec uvicorn --reload --host "$HOST" --port "$PORT" "$APP_MODULE"
