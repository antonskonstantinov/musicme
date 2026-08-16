# Muzzzic

Одностраничный веб-каталог музыкальных треков с фасетными фильтрами, поиском и аудиоплеером.

## Стек

- **Backend:** Python 3.12, Django 5, PostgreSQL 16
- **Frontend:** Vue 3, Vite, Pinia, Tailwind CSS
- **Инфраструктура:** Docker Compose

## Быстрый старт

### Требования

- Docker и Docker Compose

### Запуск

```bash
docker compose up --build
```

После запуска:

| Сервис   | URL                           |
|----------|-------------------------------|
| Frontend | http://localhost:5173/        |
| Backend  | http://localhost:8001/api/v1/ |
| Admin    | http://localhost:8001/admin/  |
| Postgres | localhost:5433                |

### Остановка

```bash
docker compose down
```

Для удаления данных PostgreSQL:

```bash
docker compose down -v
```

## Локальный запуск фронтенда

Если backend уже запущен в Docker:

```bash
cd frontend
npm install
npm run dev
```

Приложение откроется на http://localhost:5173/ и будет проксировать `/api` и `/media` на backend.

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

Код монтируется в контейнеры через volumes — изменения применяются без пересборки (hot reload).

Создание суперпользователя Django:

```bash
docker compose exec backend python manage.py createsuperuser
```

### Устранение проблем

Если `docker compose up` падает с ошибкой `address already in use`:

- **8001** — освободите порт или остановите другой сервис на нём
- **5432** — PostgreSQL в compose проброшен на **5433**, чтобы не конфликтовать с локальным Postgres
