#!/bin/bash

set -e

echo "Running migrations..."
if alembic upgrade head; then
  echo "Migrations completed successfully"
else
  echo "Migration failed"
  exit 1
fi

echo "Starting application..."
uvicorn main:app --host 0.0.0.0 --port 8000