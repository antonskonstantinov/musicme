# MusicMe

Одностраничный веб-каталог музыкальных треков с фасетными фильтрами, поиском и аудиоплеером.

## Стек

- **Backend:** Python 3.12, Django 5, Gunicorn, PostgreSQL 16
- **Frontend:** Vue 3, Vite, Pinia, Axios, Tailwind CSS, Nginx
- **Инфраструктура:** Docker Compose

## Что умеет

- Публичный каталог: жанры, настроения, артисты, альбомы, глобальный поиск
- Фасетные фильтры и список треков
- HTML5-плеер со стримингом `/media/` и перемоткой по ползунку (HTTP Range)
- Django Admin и админские API для контента
- OAuth-кнопки — заглушка («Раздел в разработке»)
- У треков: длительность из файла, текст песни, обложка из тегов mp3

## Локальная разработка

```bash
docker compose up --build
```

Миграции применяются автоматически при старте backend. Фронтенд в dev слушает **порт 5174** (не стандартный 5173).

| Сервис   | URL                           |
|----------|-------------------------------|
| Frontend | http://localhost:5174/        |
| Backend  | http://localhost:8001/api/v1/ |
| Admin    | http://localhost:8001/admin/  |
| Postgres | localhost:5433                |

Postgres (только dev): пользователь / пароль / БД — `muzzzic`.

После первого запуска каталог пустой. Создайте суперпользователя и добавьте контент:

```bash
docker compose exec backend python manage.py createsuperuser
```

Админка: http://localhost:8001/admin/ → раздел **Песни (Songs)**.

При загрузке трека:

1. **Длительность** считается из аудиофайла (mp3/wav/flac/ogg). Поле в форме скрыто. Если прочитать не удалось, появится поле «указать вручную» — без него сохранить нельзя.
2. **Текст песни** — необязательное поле. На сайте кнопка «Текст» в списке треков и в плеере открывает диалог с куплетами.
3. **Обложка** подтягивается из встроенной картинки mp3 (ID3 APIC), если она есть. Свою картинку по-прежнему можно загрузить вручную — она имеет приоритет.

Для плеера загружайте настоящие аудиофайлы (mp3/wav/flac/ogg), а не заглушки.

Остановка:

```bash
docker compose down
```

С удалением данных БД и медиа:

```bash
docker compose down -v
```

### Фронтенд на хосте

Backend должен слушать http://localhost:8001, порт **5174** свободен:

```bash
cd frontend
npm install
npm run dev
```

## Production (VPS)

Нужны Docker, Docker Compose и домен (или IP), направленный на сервер.

1. Скопируйте проект на VPS и создайте `.env` из примера:

```bash
cp .env.example .env
```

2. Заполните `.env`:

```bash
# секрет Django
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

DEBUG=0
SECRET_KEY=<сгенерированная строка>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
POSTGRES_PASSWORD=<надёжный пароль>
CORS_ALLOWED_ORIGINS=https://your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

Для проверки на сервере по IP (без домена) укажите IP в `ALLOWED_HOSTS` и `http://YOUR_IP` в `CSRF_TRUSTED_ORIGINS`.

3. Запустите production-стек (не смешивайте с `docker compose up` — у prod отдельное имя проекта `muzzzic-prod`):

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Эквивалентно: `docker-compose -f docker-compose.prod.yml up -d --build`.

Сайт: http://YOUR_DOMAIN/ (порт 80)  
Админка: http://YOUR_DOMAIN/admin/  
API: http://YOUR_DOMAIN/api/v1/

4. Создайте суперпользователя:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

5. HTTPS (позже, certbot): в `frontend/nginx.conf` есть заглушка редиректа HTTP → HTTPS и location для `/.well-known/acme-challenge/`. После выпуска сертификата раскомментируйте блок 443 и редирект, затем:

```bash
docker compose -f docker-compose.prod.yml up -d --build frontend
```

В `.env` можно включить `DJANGO_SECURE_SSL_REDIRECT=1`.

### Бэкапы

```bash
./scripts/backup.sh
```

Дамп PostgreSQL и копия `/app/media` сохраняются в `./backups/`.

### Остановка production

```bash
docker compose -f docker-compose.prod.yml down
```

## Структура проекта

```
muzzzic/
├── docker-compose.yml           # разработка
├── docker-compose.prod.yml      # VPS / production
├── .env.example
├── backend/
├── frontend/
│   ├── Dockerfile               # Vite dev
│   ├── Dockerfile.prod          # nginx + dist
│   └── nginx.conf
├── scripts/backup.sh
└── docs/
```

## Документация

- [PROJECT_VISION.md](docs/PROJECT_VISION.md) — видение проекта
- [DEVELOPMENT_PLAN.MD](docs/DEVELOPMENT_PLAN.MD) — план разработки
- [API_CONTRACT.MD](docs/API_CONTRACT.MD) — контракт API
- [DATA_MODEL.md](docs/DATA_MODEL.md) — модель данных
- [FRONTEND_SPEC.MD](docs/FRONTEND_SPEC.MD) — спецификация фронтенда

## Разработка

Код в dev-compose монтируется через volumes (hot reload). Новая npm-зависимость: `docker compose up --build frontend`.

### Устранение проблем

`address already in use`:

- **5174** — занят Vite / контейнер frontend (dev)
- **80** — занят другой nginx / production frontend
- **8001** — занят backend (dev)
- **5432** — локальный Postgres; в dev compose БД на **5433**
