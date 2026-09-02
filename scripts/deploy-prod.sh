#!/usr/bin/env bash
# Пересборка и запуск production-стека. Можно вызывать вручную и из GitHub Actions.
set -euo pipefail

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

ENV_FILE="${DEPLOY_ENV_FILE:-/opt/muzzzic/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Нет файла с секретами: $ENV_FILE" >&2
  echo "Скопируйте .env.example в этот путь и заполните значения. См. docs/DEPLOY.md" >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  compose() {
    docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml "$@"
  }
else
  compose() {
    docker-compose --env-file "$ENV_FILE" -f docker-compose.prod.yml "$@"
  }
fi

echo "Каталог проекта: $ROOT_DIR"
echo "Файл секретов:   $ENV_FILE"
echo "Собираем образы и обновляем контейнеры (тома с БД и медиа не трогаем)..."
compose up -d --build --remove-orphans

echo "Ждём ответа API на http://127.0.0.1/api/v1/ ..."
for _ in $(seq 1 45); do
  if curl -fsS --max-time 5 http://127.0.0.1/api/v1/ >/dev/null 2>&1; then
    echo "Готово: сайт должен открываться, API отвечает."
    compose ps
    exit 0
  fi
  sleep 2
done

echo "Контейнеры запущены, но API пока не ответил." >&2
echo "Смотрите логи:" >&2
echo "  docker compose --env-file $ENV_FILE -f docker-compose.prod.yml logs --tail=80" >&2
exit 1
