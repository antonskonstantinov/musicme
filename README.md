# Muzzzic

Одностраничный веб-каталог музыкальных треков с фасетными фильтрами, поиском и аудиоплеером.

Это **локальное демо / MVP**. `docker compose` поднимает Django `runserver` и Vite dev-сервер — для продакшена этого недостаточно (нет gunicorn/nginx, `DEBUG` включён, секретный ключ учебный).

## Стек

- **Backend:** Python 3.12, Django 5, Django REST Framework, PostgreSQL 16
- **Frontend:** Vue 3, Vite, Pinia, Axios, Tailwind CSS
- **Инфраструктура:** Docker Compose

## Что умеет

- Публичный каталог: жанры, настроения, артисты, альбомы, глобальный поиск
- Фасетные фильтры и список треков
- HTML5-плеер со стримингом `/media/`
- Django Admin и админские API для контента
- OAuth-кнопки — заглушка («Раздел в разработке»)

## Требования

- Docker и Docker Compose

## Запуск

```bash
docker compose up --build
```

Миграции применяются автоматически при старте backend (`entrypoint.sh`).

После запуска:

| Сервис   | URL                           |
|----------|-------------------------------|
| Frontend | http://localhost:5173/        |
| Backend  | http://localhost:8001/api/v1/ |
| Admin    | http://localhost:8001/admin/  |
| Postgres | localhost:5433                |

Учётные данные Postgres (только для локальной разработки): пользователь / пароль / БД — `muzzzic`.

### После первого запуска каталог пустой

Без данных в админке главная покажет «Контент скоро появится».

1. Создайте суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

2. Войдите в http://localhost:8001/admin/
3. Добавьте жанры, настроения, исполнителей, альбомы и песни.
4. Для песен загрузите **настоящие** аудиофайлы (mp3/wav/flac/ogg). Заглушки браузер не воспроизведёт.

### Остановка

```bash
docker compose down
```

Удалить данные PostgreSQL и загруженные медиа:

```bash
docker compose down -v
```

## Локальный запуск фронтенда (без контейнера frontend)

Backend должен быть доступен на http://localhost:8001 (контейнер `backend`). Порт **5173** не должен быть занят контейнером `frontend`.

```bash
cd frontend
npm install
npm run dev
```

Vite проксирует `/api` и `/media` на `http://127.0.0.1:8001`.

## Структура проекта

```
muzzzic/
├── docker-compose.yml
├── backend/          # Django API
├── frontend/         # Vue SPA
└── docs/             # Спецификации
```

## Документация

- [PROJECT_VISION.md](docs/PROJECT_VISION.md) — видение проекта
- [DEVELOPMENT_PLAN.MD](docs/DEVELOPMENT_PLAN.MD) — план разработки
- [API_CONTRACT.MD](docs/API_CONTRACT.MD) — контракт API
- [DATA_MODEL.md](docs/DATA_MODEL.md) — модель данных
- [FRONTEND_SPEC.MD](docs/FRONTEND_SPEC.MD) — спецификация фронтенда

## Разработка

Код монтируется в контейнеры через volumes — изменения применяются без пересборки (hot reload). Если на фронтенде добавили npm-зависимость, пересоберите сервис: `docker compose up --build frontend`.

### Устранение проблем

Если `docker compose up` падает с ошибкой `address already in use`:

- **5173** — занят другой Vite / контейнер frontend
- **8001** — занят другой backend
- **5432** — локальный Postgres; в compose БД проброшена на **5433**
