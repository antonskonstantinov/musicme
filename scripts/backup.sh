#!/bin/sh
set -e

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose -f docker-compose.prod.yml"
else
  COMPOSE="docker-compose -f docker-compose.prod.yml"
fi
STAMP=$(date -u +"%Y%m%dT%H%M%SZ")
BACKUP_DIR=${BACKUP_DIR:-"$ROOT_DIR/backups"}

mkdir -p "$BACKUP_DIR"

echo "Dumping PostgreSQL..."
$COMPOSE exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  > "$BACKUP_DIR/db-$STAMP.sql"

echo "Copying media volume..."
$COMPOSE cp backend:/app/media "$BACKUP_DIR/media-$STAMP"

echo "Backup saved in $BACKUP_DIR"
