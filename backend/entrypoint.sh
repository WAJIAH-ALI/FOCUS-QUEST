#!/bin/sh
set -e

# Run database migrations if starting the API server (uvicorn) or explicitly requested
if [ "$1" = "uvicorn" ] || [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "================================================="
    echo "==> Running Alembic migrations on Postgres... <=="
    echo "================================================="
    alembic upgrade head
    echo "==> Migrations applied successfully!            <=="
    echo "================================================="
fi

exec "$@"
