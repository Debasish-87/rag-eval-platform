#!/bin/sh
set -e

# --- Wait for Postgres (skip entirely for SQLite) ---
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q '^postgresql'; then
  echo "Waiting for Postgres..."
  python <<'PYEOF'
import os
import sys
import time

import sqlalchemy

url = os.environ["DATABASE_URL"]
deadline = time.time() + 60

while time.time() < deadline:
    try:
        engine = sqlalchemy.create_engine(url)
        with engine.connect():
            print("Postgres is ready.")
            sys.exit(0)
    except Exception:
        time.sleep(1)

print("Postgres did not become ready in time.", file=sys.stderr)
sys.exit(1)
PYEOF
fi

# --- Apply migrations ---
echo "Running database migrations..."
alembic upgrade head

# --- Optionally seed demo data on first boot ---
if [ "${SEED_ON_START:-true}" = "true" ]; then
  echo "Seeding demo benchmark (SEED_ON_START=true)..."
  python scripts/run_evaluation.py --experiment "${SEED_EXPERIMENT_NAME:-gemini-flash}" || true
fi

echo "Starting: $@"
exec "$@"
