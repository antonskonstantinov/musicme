#!/usr/bin/env bash
# Регистрирует уже установленный runner в репозитории GitHub.
# Запускать от пользователя github-runner, НЕ от root.
set -euo pipefail

if [[ "$(id -u)" -eq 0 ]]; then
  echo "Не запускайте этот скрипт от root. GitHub запрещает регистрировать runner с правами администратора." >&2
  echo "Пример: sudo -u github-runner bash scripts/register-github-runner.sh --url ... --token ..." >&2
  exit 1
fi

RUNNER_DIR="${RUNNER_DIR:-/opt/actions-runner}"
RUNNER_NAME="${RUNNER_NAME:-muzzzic-prod}"
RUNNER_LABELS="${RUNNER_LABELS:-muzzzic-prod}"
REPO_URL=""
TOKEN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      REPO_URL="$2"
      shift 2
      ;;
    --token)
      TOKEN="$2"
      shift 2
      ;;
    --name)
      RUNNER_NAME="$2"
      shift 2
      ;;
    --labels)
      RUNNER_LABELS="$2"
      shift 2
      ;;
    --dir)
      RUNNER_DIR="$2"
      shift 2
      ;;
    *)
      echo "Неизвестный аргумент: $1" >&2
      echo "Нужно: --url https://github.com/owner/repo --token РЕГИСТРАЦИОННЫЙ_ТОКЕН" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_URL" || -z "$TOKEN" ]]; then
  echo "Нужны --url и --token. Токен берётся в GitHub: Settings → Actions → Runners → New self-hosted runner." >&2
  exit 1
fi

if [[ ! -x "$RUNNER_DIR/config.sh" ]]; then
  echo "Не найден $RUNNER_DIR/config.sh. Сначала выполните scripts/install-github-runner.sh от root." >&2
  exit 1
fi

cd "$RUNNER_DIR"
./config.sh \
  --unattended \
  --replace \
  --url "$REPO_URL" \
  --token "$TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "$RUNNER_LABELS" \
  --work _work

echo
echo "Runner зарегистрирован как «$RUNNER_NAME» с меткой «$RUNNER_LABELS»."
echo "Теперь от пользователя с sudo:"
echo "  cd $RUNNER_DIR"
echo "  sudo ./svc.sh install $(id -un)"
echo "  sudo ./svc.sh start"
echo "  sudo ./svc.sh status"
