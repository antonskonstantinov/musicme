#!/usr/bin/env bash
# Ставит GitHub Actions runner в /opt/actions-runner (нужен root).
# Не регистрирует его в GitHub — это следующий шаг, см. docs/DEPLOY.md.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Запустите скрипт от root: sudo bash scripts/install-github-runner.sh" >&2
  exit 1
fi

RUNNER_USER="${RUNNER_USER:-github-runner}"
RUNNER_DIR="${RUNNER_DIR:-/opt/actions-runner}"
FALLBACK_VERSION="2.336.0"

if ! command -v docker >/dev/null 2>&1; then
  echo "Сначала установите Docker и Docker Compose. См. docs/DEPLOY.md, раздел «Что должно быть на сервере»." >&2
  exit 1
fi

if ! getent group docker >/dev/null; then
  echo "Группа docker не найдена. Docker установлен не полностью." >&2
  exit 1
fi

if ! id -u "$RUNNER_USER" >/dev/null 2>&1; then
  useradd --system --create-home --shell /bin/bash "$RUNNER_USER"
  echo "Создан пользователь $RUNNER_USER"
fi

usermod -aG docker "$RUNNER_USER"

mkdir -p "$RUNNER_DIR"
if [[ -e "$RUNNER_DIR/config.sh" ]]; then
  echo "Runner уже распакован в $RUNNER_DIR — пропускаю загрузку."
else
  echo "Узнаём последнюю версию runner с GitHub..."
  TAG=$(curl -fsSL https://api.github.com/repos/actions/runner/releases/latest \
    | grep -o '"tag_name": *"[^"]*"' | head -1 | cut -d'"' -f4 || true)
  VERSION="${TAG#v}"
  if [[ -z "$VERSION" ]]; then
    VERSION="$FALLBACK_VERSION"
    echo "Не удалось спросить GitHub API, берём версию $VERSION"
  fi

  ARCHIVE="actions-runner-linux-x64-${VERSION}.tar.gz"
  URL="https://github.com/actions/runner/releases/download/v${VERSION}/${ARCHIVE}"
  echo "Скачиваем $URL"
  curl -fL -o "/tmp/${ARCHIVE}" "$URL"
  tar -xzf "/tmp/${ARCHIVE}" -C "$RUNNER_DIR"
  rm -f "/tmp/${ARCHIVE}"
fi

if [[ -x "$RUNNER_DIR/bin/installdependencies.sh" ]]; then
  echo "Ставим системные зависимости runner..."
  "$RUNNER_DIR/bin/installdependencies.sh"
fi

chown -R "$RUNNER_USER:$RUNNER_USER" "$RUNNER_DIR"

echo
echo "Готово. Дальше — регистрация в GitHub (раздел 4 в docs/DEPLOY.md):"
echo "  1. Откройте репозиторий → Settings → Actions → Runners → New self-hosted runner"
echo "  2. Скопируйте Registration token (живёт около часа)"
echo "  3. Из каталога клона проекта (обычно /opt/muzzzic) выполните:"
echo "     sudo -u $RUNNER_USER bash scripts/register-github-runner.sh \\"
echo "       --url https://github.com/ВЛАДЕЛЕЦ/РЕПОЗИТОРИЙ \\"
echo "       --token ВСТАВЬТЕ_ТОКЕН"
echo
echo "После регистрации:"
echo "  cd $RUNNER_DIR && sudo ./svc.sh install $RUNNER_USER && sudo ./svc.sh start"
echo "  sudo ./svc.sh status"
