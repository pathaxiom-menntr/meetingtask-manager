#!/bin/sh
# entrypoint.sh — runs inside the container on every startup
# 1. Runs Alembic migrations (idempotent — safe to run on every deploy)
# 2. Starts Gunicorn with Uvicorn workers

set -e

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Starting Gunicorn..."
exec gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers "${WORKERS:-2}" \
  --bind "0.0.0.0:${PORT:-8000}" \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level "${LOG_LEVEL:-info}"
