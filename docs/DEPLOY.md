# Автодеплой MusicMe на production

Эта инструкция для человека, который администрирует VPS и ещё не настраивал CI/CD.
После настройки каждый `git push` в ветку `main` сам обновит сайт на сервере.

## Зачем это нужно

Раньше сайт обновляли вручную: зайти на сервер по SSH, подтянуть код, пересобрать Docker.
Теперь цепочка такая:

1. Разработчик пушит коммит в ветку `main` на GitHub.
2. GitHub Actions видит push и ставит задание «задеплоить».
3. На **вашем** VPS крутится программа **self-hosted runner** (раннер). Она постоянно спрашивает GitHub: «есть работа?».
4. Раннер забирает свежий код и запускает тот же `docker compose`, что и при ручном деплое.

Раннер стоит именно на проде, а не в облаке GitHub, потому что секреты (`.env`), Docker-тома с базой и медиа-файлы уже лежат на этом сервере. Облачный раннер до них не доберётся.

```
  ноутбук                GitHub                  VPS (production)
  git push main  →  Actions: job «deploy»  →  runner видит job
                                              →  checkout кода
                                              →  docker compose up -d --build
                                              →  сайт обновлён
```

Никаких новых портов снаружи открывать не нужно: раннер сам ходит **исходящим** HTTPS на `github.com`.

---

## Что должно быть на сервере до начала

Чеклист. Если чего-то нет — сначала это, потом раннер.

- [ ] Ubuntu (или похожий Linux), доступ по SSH с `sudo`
- [ ] Установлены Docker и Docker Compose plugin (`docker compose version` печатает версию)
- [ ] Репозиторий MusicMe уже клонирован, например в `/opt/muzzzic`
- [ ] Production уже один раз запускали: есть файл **`/opt/muzzzic/.env`** с боевыми секретами и работает

  ```bash
  docker compose -f docker-compose.prod.yml --env-file /opt/muzzzic/.env ps
  ```

- [ ] Код лежит на GitHub, основная ветка называется `main`
- [ ] У вас есть права **Admin** в репозитории (без них не создать runner)

`.env` **никогда** не коммитится в git. Раннер только читает его с диска.

Если проекта на сервере ещё нет — сначала раздел [Production (VPS)](../README.md#production-vps) в README, потом вернитесь сюда.

Пути, которые дальше считаются стандартными (если у вас иначе — замените везде):

| Что | Путь |
|-----|------|
| Клон репозитория | `/opt/muzzzic` |
| Секреты production | `/opt/muzzzic/.env` |
| GitHub runner | `/opt/actions-runner` |
| Системный пользователь раннера | `github-runner` |

Файл `.github/workflows/deploy.yml` уже зашивает путь `/opt/muzzzic/.env`. Сменили каталог — поправьте `DEPLOY_ENV_FILE` в этом workflow.

---

## Этап 1. Подготовить каталоги и код на сервере

Под пользователем с `sudo`:

```bash
sudo mkdir -p /opt/muzzzic
sudo chown "$USER:$USER" /opt/muzzzic
cd /opt/muzzzic
```

Если клона ещё нет:

```bash
git clone https://github.com/ВЛАДЕЛЕЦ/РЕПОЗИТОРИЙ.git /opt/muzzzic
cd /opt/muzzzic
git checkout main
```

Если клон уже есть — просто `git pull`.

Секреты (один раз, если файла ещё нет):

```bash
cp .env.example /opt/muzzzic/.env
nano /opt/muzzzic/.env
```

Чтобы файл не попал в git и его мог прочитать раннер (он будет в группе `docker`):

```bash
sudo chmod 640 /opt/muzzzic/.env
sudo chown root:docker /opt/muzzzic/.env
```

Дальше файл правят так: `sudo nano /opt/muzzzic/.env`.

Проверьте, что прод поднимается вручную — это те же команды, что потом вызовет Actions:

```bash
cd /opt/muzzzic
bash scripts/deploy-prod.sh
```

Если скрипт написал «Готово» и сайт открывается — можно ставить раннер.

---

## Этап 2. Включить Actions в репозитории GitHub

В браузере:

1. Откройте репозиторий на GitHub.
2. **Settings** (настройки репозитория, не профиля).
3. Слева **Actions** → **General**.
4. **Actions permissions**: разрешите Actions (обычно «Allow all actions and reusable workflows»).
5. Прокрутите до **Runner group** / **Run workflows**: оставьте запуск из ветки `main`.
6. Сохраните **Save**.

Файл `.github/workflows/deploy.yml` должен быть **в ветке `main`**. Если вы только что его добавили локально — закоммитьте и запушьте (это ещё не автодеплой: раннера пока нет, job подождёт в очереди).

---

## Этап 3. Поставить runner на VPS

На сервере, из каталога проекта, **от root**:

```bash
cd /opt/muzzzic
sudo bash scripts/install-github-runner.sh
```

Скрипт:

- создаёт пользователя `github-runner`;
- добавляет его в группу `docker` (чтобы собирать контейнеры без root);
- качает программу runner в `/opt/actions-runner`.

Он **не** привязывает сервер к GitHub — не хватает одноразового токена.

---

## Этап 4. Зарегистрировать runner в GitHub

Токен выдаёт только сайт GitHub и живёт **около часа**. Не сохраняйте его в git и в `.env`.

1. Репозиторий → **Settings** → **Actions** → **Runners**.
2. Кнопка **New self-hosted runner**.
3. OS: **Linux**, Architecture: **x64**.
4. На странице будет блок с токеном (`--token AAAA...`). Скопируйте только токен, не всю простыню команд — команды уже есть в наших скриптах.
5. На сервере (подставьте свой URL репозитория и токен):

```bash
cd /opt/muzzzic
sudo -u github-runner bash scripts/register-github-runner.sh \
  --url https://github.com/ВЛАДЕЛЕЦ/РЕПОЗИТОРИЙ \
  --token ВСТАВЬТЕ_ТОКЕН
```

Если токен протух — снова **New self-hosted runner** и новый токен. Переустанавливать `/opt/actions-runner` не нужно.

Имя раннера и метка по умолчанию: `muzzzic-prod`. Workflow ищет именно метку `muzzzic-prod`. Не меняйте её без правки `.github/workflows/deploy.yml`.

---

## Этап 5. Включить runner как службу (чтобы жил после перезагрузки)

`config.sh` нельзя было запускать от root, а службу — наоборот, ставит root:

```bash
cd /opt/actions-runner
sudo ./svc.sh install github-runner
sudo ./svc.sh start
sudo ./svc.sh status
```

Ожидаете строку вроде `active (running)`.

На GitHub: **Settings** → **Actions** → **Runners** — раннер **Idle** (зелёный, ждёт работу). Если **Offline** — см. раздел «Если что-то пошло не так».

Полезные команды:

```bash
cd /opt/actions-runner
sudo ./svc.sh status
sudo journalctl -u 'actions.runner.*' -e
```

---

## Этап 6. Первый деплой через GitHub

Два способа проверить, что цепочка живая.

**Вариант А — кнопка (ничего не пушить):**

1. GitHub → вкладка **Actions**.
2. Слева workflow **Deploy production**.
3. Справа **Run workflow** → ветка `main` → **Run workflow**.

**Вариант Б — обычный push в `main`:**

```bash
git checkout main
git add .github/workflows/deploy.yml scripts/deploy-prod.sh docs/DEPLOY.md
git commit -m "Включить автодеплой на production"
git push origin main
```

Зайдите в **Actions**: должен появиться жёлтый кружок (идёт job), затем зелёная галочка.

На сервере во время job можно смотреть:

```bash
sudo journalctl -u 'actions.runner.*' -f
docker compose -f /opt/muzzzic/docker-compose.prod.yml --env-file /opt/muzzzic/.env ps
```

Важно: job выполняется **не** в `/opt/muzzzic`, а в рабочем каталоге раннера (`/opt/actions-runner/_work/...`). Оттуда собираются новые образы. Контейнеры и тома называются `muzzzic-prod` — база и `/app/media` **не удаляются**.

Пуши только в `docs/` или `*.md` workflow **пропускает** (сайт от этого не меняется). Чтобы прогнать деплой без правки кода — **Run workflow**.

---

## Что делает workflow

Файл: `.github/workflows/deploy.yml`

| Шаг | Смысл |
|-----|--------|
| Срабатывает на push в `main` или на **Run workflow** | Не на `develop` и не на pull request |
| `runs-on: [self-hosted, muzzzic-prod]` | Берёт только ваш VPS, не облачные машины GitHub |
| `actions/checkout` | Скачивает коммит, который запушили |
| `scripts/deploy-prod.sh` | `docker compose -f docker-compose.prod.yml up -d --build` + проверка `http://127.0.0.1/api/v1/` |

Миграции Django и `collectstatic` по-прежнему делает `backend/entrypoint.sh` при старте контейнера.

Одновременно два деплоя не бегут: второй ждёт первого (`concurrency`).

---

## Повседневная работа

Разработчик:

```bash
git checkout main
# …правки…
git push origin main
```

DevOps смотрит **Actions**. Если красный крест — открыть упавший шаг, читать лог.

Откатить сайт на предыдущий коммит: `git revert` на `main` и снова push (или `git reset` + force-push, только если команда это осознанно делает).

Ручной деплой без GitHub (если Actions лежит):

```bash
cd /opt/muzzzic
git fetch origin
git checkout main
git pull
bash scripts/deploy-prod.sh
```

---

## Если что-то пошло не так

**Job висит «Queued» / Waiting for a runner**

- Раннер Offline: `cd /opt/actions-runner && sudo ./svc.sh start`
- Метка не `muzzzic-prod`: в Runners откройте раннер и проверьте Labels
- Actions выключены в Settings → Actions → General

**Runner Offline**

```bash
cd /opt/actions-runner
sudo ./svc.sh status
sudo journalctl -u 'actions.runner.*' -e --no-pager | tail -50
```

Частые причины: сервер без интернета, GitHub недоступен, служба не ставили (`svc.sh install`).

**Permission denied / cannot connect to Docker socket**

Пользователь `github-runner` не в группе `docker`:

```bash
sudo usermod -aG docker github-runner
cd /opt/actions-runner && sudo ./svc.sh stop && sudo ./svc.sh start
```

**Нет файла /opt/muzzzic/.env**

Скрипт деплоя так и напишет. Создайте файл, проверьте права (группа `docker` или владелец `github-runner`).

**Сборка падает, старый сайт**

При ошибке `build` Compose обычно не подменяет работающие контейнеры. Чините код, пушьте снова. Логи: вкладка Actions и `docker compose ... logs`.

**Токен регистрации invalid**

Прошёл час. Новый токен на странице New self-hosted runner, снова `register-github-runner.sh`. Флаг `--replace` в скрипте перезапишет старую регистрацию с тем же именем.

**Случайно запустили install/config от root**

`config.sh` откажется. Ничего страшного: повторите от `github-runner`.

---

## Снять runner (если сервер меняете)

```bash
cd /opt/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh uninstall
sudo -u github-runner ./config.sh remove --token НОВЫЙ_ТОКЕН_С_СТРАНИЦЫ_REMOVE
```

Токен на снятие снова берётся в Settings → Runners у этого раннера.

---

## Безопасность (коротко)

- Кто может пушить в `main`, тот де-факто деплоит прод. Защитите ветку: Settings → Branches → **Add branch protection rule** для `main` (хотя бы «Require a pull request», если работаете не в одиночку).
- Self-hosted runner выполняет всё, что написано в workflow, с правами `github-runner` и доступом к Docker. Не ставьте этот runner на репозиторий, куда могут пушить посторонние (форки).
- Не кладите `SECRET_KEY` и пароль БД в workflow и в GitHub Secrets — они уже в `/opt/muzzzic/.env` на диске.
- Регистрационный токен runner ≠ Personal Access Token. Его нельзя переиспользовать через неделю.

---

## Файлы в репозитории

| Файл | Назначение |
|------|------------|
| `.github/workflows/deploy.yml` | Когда и что запускать после push в `main` |
| `scripts/deploy-prod.sh` | Сборка и перезапуск Docker Compose + проверка API |
| `scripts/install-github-runner.sh` | Один раз: пользователь и бинарники runner (root) |
| `scripts/register-github-runner.sh` | Один раз: привязка к репозиторию (не root) |
