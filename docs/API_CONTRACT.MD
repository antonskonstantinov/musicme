# API CONTRACT — MusicMe

## 1. Общие положения

### 1.1. Базовые принципы
- **Формат:** JSON (application/json)
- **Версия:** `/api/v1/`
- **Аутентификация публичных эндпоинтов:** Не требуется
- **Аутентификация админских эндпоинтов:** Django Session (Django Admin)
- **Кодировка:** UTF-8

### 1.2. Формат ответа (Success)

```json
{
  "data": { ... } | [ ... ],
  "meta": {
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
Примечание: Для списков используем пагинацию. Для одиночных объектов meta опускается.

1.3. Формат ошибки
json
{
  "error": {
    "code": "validation_error",
    "message": "Некорректные данные",
    "details": {
      "title": ["Это поле обязательно."]
    }
  }
}
1.4. Коды ответов
Код	Описание
200	Успешный запрос
201	Ресурс создан
204	Ресурс удалён (без тела ответа)
400	Ошибка валидации
401	Требуется аутентификация
403	Недостаточно прав
404	Ресурс не найден
405	Метод не поддерживается
500	Внутренняя ошибка сервера
2. Публичные эндпоинты (без аутентификации)
2.1. Список жанров
GET /api/v1/genres/

Ответ 200:

json
{
  "data": [
    { "id": 1, "name": "Hip-Hop" },
    { "id": 2, "name": "Rock" },
    { "id": 3, "name": "Jazz" },
    { "id": 4, "name": "Electronic" }
  ],
  "meta": {
    "total": 4,
    "page": 1,
    "page_size": 100
  }
}
Примечание: Список жанров не фильтруется, всегда отдаём все (справочник небольшой).

2.2. Список настроений
GET /api/v1/moods/

Ответ 200:

json
{
  "data": [
    { "id": 1, "name": "Грустное" },
    { "id": 2, "name": "Весёлое" },
    { "id": 3, "name": "Энергичное" },
    { "id": 4, "name": "Меланхоличное" }
  ],
  "meta": {
    "total": 4,
    "page": 1,
    "page_size": 100
  }
}
Примечание: Список настроений не фильтруется, всегда отдаём все (справочник небольшой).

2.3. Список исполнителей (фасетный поиск)
GET /api/v1/artists/

Query Parameters:

Параметр	Тип	Обязательный	Описание
genre_id	int	Нет	Фильтр: исполнители, у которых есть песни с этим жанром
mood_id	int	Нет	Фильтр: исполнители, у которых есть песни с этим настроением
search	string	Нет	Поиск по имени исполнителя (частичное совпадение, регистронезависимо)
Примеры запросов:

text
GET /api/v1/artists/
GET /api/v1/artists/?genre_id=1
GET /api/v1/artists/?mood_id=2
GET /api/v1/artists/?genre_id=1&mood_id=2
GET /api/v1/artists/?search=мот
GET /api/v1/artists/?genre_id=1&mood_id=2&search=мот
Ответ 200:

json
{
  "data": [
    {
      "id": 1,
      "name": "Мот",
      "albums_count": 5
    },
    {
      "id": 2,
      "name": "Баста",
      "albums_count": 8
    }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "page_size": 20
  }
}
Логика фильтрации (фасетный поиск):

Все параметры опциональны и НЕЗАВИСИМЫ

Без параметров — возвращаются все артисты (с пагинацией)

Если указан genre_id — отбираются артисты, у которых есть хотя бы одна песня с данным жанром (через AlbumSong → Song → SongGenre)

Если указан mood_id — аналогично для настроения (через AlbumSong → Song → SongMood)

Если указаны оба — условия объединяются через AND

search — поиск по полю name (case-insensitive, содержит подстроку)

Несколько параметров объединяются через AND

2.4. Список альбомов (фасетный поиск)
GET /api/v1/albums/

Query Parameters:

Параметр	Тип	Обязательный	Описание
artist_id	int	Нет	Фильтр по исполнителю
genre_id	int	Нет	Фильтр: альбомы, содержащие песни с этим жанром
mood_id	int	Нет	Фильтр: альбомы, содержащие песни с этим настроением
search	string	Нет	Поиск по названию альбома и имени исполнителя
year_from	int	Нет	Год выпуска: от (включительно)
year_to	int	Нет	Год выпуска: до (включительно)
Примеры запросов:

text
GET /api/v1/albums/
GET /api/v1/albums/?artist_id=1
GET /api/v1/albums/?genre_id=2
GET /api/v1/albums/?artist_id=1&genre_id=2
GET /api/v1/albums/?artist_id=1&genre_id=2&mood_id=3
GET /api/v1/albums/?search=хиты
GET /api/v1/albums/?year_from=2010&year_to=2023
Ответ 200:

json
{
  "data": [
    {
      "id": 10,
      "title": "Лучшие хиты",
      "year": 2023,
      "cover_url": "/media/covers/album_10.jpg",
      "artist": {
        "id": 1,
        "name": "Мот"
      },
      "tracks_count": 14
    },
    {
      "id": 11,
      "title": "Соло",
      "year": 2021,
      "cover_url": null,
      "artist": {
        "id": 1,
        "name": "Мот"
      },
      "tracks_count": 9
    }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "page_size": 20
  }
}
Логика фильтрации (фасетный поиск):

Все параметры опциональны и НЕЗАВИСИМЫ

Без параметров — возвращаются все альбомы (с пагинацией)

Если указан artist_id — отбираются альбомы этого исполнителя

Если указан genre_id — отбираются альбомы, содержащие хотя бы одну песню с данным жанром

Если указан mood_id — отбираются альбомы, содержащие хотя бы одну песню с данным настроением

search — ищет по Album.title и Artist.name (case-insensitive, содержит подстроку)

Несколько параметров объединяются через AND

Если cover_url = null — фронтенд показывает placeholder

2.5. Глобальный поиск
GET /api/v1/search/

Query Parameters:

Параметр	Тип	Обязательный	Описание
query	string	Да	Поисковый запрос (мин. 2 символа)
Пример запроса:

text
GET /api/v1/search/?query=мот
Ответ 200:

json
{
  "data": {
    "artists": [
      {
        "id": 1,
        "name": "Мот",
        "albums_count": 5
      }
    ],
    "albums": [
      {
        "id": 10,
        "title": "Лучшие хиты",
        "year": 2023,
        "cover_url": "/media/covers/album_10.jpg",
        "artist_id": 1,
        "artist_name": "Мот"
      }
    ],
    "songs": [
      {
        "id": 100,
        "title": "Капкан",
        "duration_seconds": 210,
        "lyrics": "Первый куплет\n\nПрипев",
        "audio_url": "/media/audio/song_100.mp3",
        "album_id": 10,
        "album_title": "Лучшие хиты",
        "artist_name": "Мот"
      }
    ]
  },
  "meta": {
    "total_artists": 1,
    "total_albums": 1,
    "total_songs": 1
  }
}
Логика:

Поиск по Song.title (частичное совпадение, case-insensitive)

Поиск по Artist.name (частичное совпадение, case-insensitive)

Поиск по Album.title (частичное совпадение, case-insensitive)

Минимальная длина запроса — 2 символа

Если query короче 2 символов — возвращается 400

Ошибка 400 (короткий запрос):

json
{
  "error": {
    "code": "validation_error",
    "message": "Поисковый запрос должен содержать минимум 2 символа",
    "details": {}
  }
}
2.6. Детали альбома с треками
GET /api/v1/albums/{album_id}/

Ответ 200:

json
{
  "data": {
    "id": 10,
    "title": "Лучшие хиты",
    "year": 2023,
    "cover_url": "/media/covers/album_10.jpg",
    "description": "Сборник главных треков. Короткие истории про ночной город.",
    "artist": {
      "id": 1,
      "name": "Мот"
    },
    "tracks": [
      {
        "id": 100,
        "title": "Капкан",
        "track_number": 1,
        "duration_seconds": 210,
        "lyrics": "Первый куплет\n\nПрипев",
        "audio_url": "/media/audio/song_100.mp3",
        "cover_url": "/media/covers/song_100.jpg",
        "genres": [
          { "id": 1, "name": "Hip-Hop" }
        ],
        "moods": [
          { "id": 2, "name": "Энергичное" }
        ]
      },
      {
        "id": 101,
        "title": "Соло",
        "track_number": 2,
        "duration_seconds": 185,
        "lyrics": "",
        "audio_url": "/media/audio/song_101.mp3",
        "cover_url": null,
        "genres": [
          { "id": 1, "name": "Hip-Hop" },
          { "id": 3, "name": "Jazz" }
        ],
        "moods": [
          { "id": 2, "name": "Энергичное" },
          { "id": 4, "name": "Меланхоличное" }
        ]
      }
    ]
  }
}
Логика:

Треки отсортированы по track_number (по возрастанию)

Если у песни нет своей обложки — cover_url = null (фронтенд подставит обложку альбома)

lyrics — текст песни (может быть пустой строкой)

description — краткое описание альбома (может быть пустой строкой, до 500 символов)

audio_url и cover_url — относительные пути (фронтенд добавляет базовый URL)

Ошибка 404:

json
{
  "error": {
    "code": "not_found",
    "message": "Альбом не найден",
    "details": {}
  }
}
2.7. Стриминг аудио
GET /media/audio/{filename}

Ответ: Бинарный поток аудиофайла с заголовками:

text
Content-Type: audio/mpeg
Accept-Ranges: bytes
Логика:

Поддержка HTTP Range для частичной загрузки (seek в плеере)

Файлы отдаются статически (nginx / Django static / Whitenoise)

3. Административные эндпоинты (только для админа)
3.1. CRUD: Исполнители
Метод	Эндпоинт	Описание
GET	/api/v1/admin/artists/	Список исполнителей (с пагинацией)
POST	/api/v1/admin/artists/	Создать исполнителя
GET	/api/v1/admin/artists/{id}/	Детали исполнителя
PUT	/api/v1/admin/artists/{id}/	Полное обновление
PATCH	/api/v1/admin/artists/{id}/	Частичное обновление
DELETE	/api/v1/admin/artists/{id}/	Удалить исполнителя
POST /api/v1/admin/artists/

Тело запроса:

json
{
  "name": "Новый Артист"
}
Ответ 201:

json
{
  "data": {
    "id": 2,
    "name": "Новый Артист",
    "albums_count": 0,
    "created_at": "2025-01-15T12:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
}
Валидация:

name — обязательное (1-200 символов), уникальное

3.2. CRUD: Альбомы
Метод	Эндпоинт	Описание
GET	/api/v1/admin/albums/	Список альбомов
POST	/api/v1/admin/albums/	Создать альбом
GET	/api/v1/admin/albums/{id}/	Детали альбома
PUT	/api/v1/admin/albums/{id}/	Полное обновление
PATCH	/api/v1/admin/albums/{id}/	Частичное обновление
DELETE	/api/v1/admin/albums/{id}/	Удалить альбом
POST /api/v1/admin/albums/

Тело запроса (multipart/form-data):

json
{
  "title": "Новый Альбом",
  "artist_id": 1,
  "year": 2024,
  "description": "Краткое описание альбома (опционально)",
  "cover": "<файл изображения>"
}
Ответ 201:

json
{
  "data": {
    "id": 11,
    "title": "Новый Альбом",
    "year": 2024,
    "description": "Краткое описание альбома (опционально)",
    "cover_url": "/media/covers/album_11.jpg",
    "artist": {
      "id": 1,
      "name": "Мот"
    },
    "created_at": "2025-01-15T12:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
}
Валидация:

title — обязательное (1-200 символов)

artist_id — обязательное, существующий артист

year — опциональное (1800-2100)

cover — опциональное (jpg, png, webp; макс. 5 MB)

description — опциональное (текст, до 500 символов)

Уникальность: (artist_id, title) — у одного исполнителя не может быть двух альбомов с одинаковым названием

3.3. CRUD: Песни
Метод	Эндпоинт	Описание
GET	/api/v1/admin/songs/	Список песен
POST	/api/v1/admin/songs/	Создать песню
GET	/api/v1/admin/songs/{id}/	Детали песни
PUT	/api/v1/admin/songs/{id}/	Полное обновление
PATCH	/api/v1/admin/songs/{id}/	Частичное обновление
DELETE	/api/v1/admin/songs/{id}/	Удалить песню
POST /api/v1/admin/songs/

Тело запроса (multipart/form-data):

json
{
  "title": "Новая Песня",
  "audio_file": "<файл аудио>",
  "lyrics": "Текст песни (опционально)",
  "cover": "<файл изображения (опционально)>",
  "genre_ids": [1, 2],
  "mood_ids": [2, 3],
  "album_assignments": [
    { "album_id": 10, "track_number": 3 }
  ]
}
Ответ 201:

json
{
  "data": {
    "id": 102,
    "title": "Новая Песня",
    "duration_seconds": 215,
    "lyrics": "Текст песни (опционально)",
    "audio_url": "/media/audio/song_102.mp3",
    "cover_url": null,
    "genres": [
      { "id": 1, "name": "Hip-Hop" },
      { "id": 2, "name": "Rock" }
    ],
    "moods": [
      { "id": 2, "name": "Весёлое" },
      { "id": 3, "name": "Энергичное" }
    ],
    "albums": [
      { "album_id": 10, "track_number": 3 }
    ],
    "created_at": "2025-01-15T12:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
}
Валидация:

title — обязательное (1-200 символов)

audio_file — обязательное (mp3, wav, flac, ogg; макс. 20 MB)

duration_seconds — не передавать при создании: берётся из аудиофайла. Обязательно (>= 0) только если длительность из файла прочитать не удалось

lyrics — опциональное (текст песни, до 50 000 символов)

cover — опциональное (jpg, png, webp; макс. 5 MB). Если не передано, а в mp3 есть встроенная картинка (ID3 APIC) — обложка берётся из файла

genre_ids — опциональное, массив ID существующих жанров

mood_ids — опциональное, массив ID существующих настроений

album_assignments — опциональное, массив объектов с album_id и track_number

3.4. Управление жанрами (справочник)
Метод	Эндпоинт	Описание
GET	/api/v1/admin/genres/	Список жанров
POST	/api/v1/admin/genres/	Создать жанр
DELETE	/api/v1/admin/genres/{id}/	Удалить жанр
POST /api/v1/admin/genres/

Тело запроса:

json
{
  "name": "Lo-Fi"
}
Ответ 201:

json
{
  "data": {
    "id": 5,
    "name": "Lo-Fi",
    "created_at": "2025-01-15T12:00:00Z"
  }
}
Валидация:

name — обязательное (1-100 символов), уникальное

3.5. Управление настроениями (справочник)
Метод	Эндпоинт	Описание
GET	/api/v1/admin/moods/	Список настроений
POST	/api/v1/admin/moods/	Создать настроение
DELETE	/api/v1/admin/moods/{id}/	Удалить настроение
POST /api/v1/admin/moods/

Тело запроса:

json
{
  "name": "Задумчивое"
}
Ответ 201:

json
{
  "data": {
    "id": 5,
    "name": "Задумчивое",
    "created_at": "2025-01-15T12:00:00Z"
  }
}
Валидация:

name — обязательное (1-100 символов), уникальное

3.6. Управление связью Альбом ↔ Песня
Метод	Эндпоинт	Описание
POST	/api/v1/admin/albums/{album_id}/tracks/	Добавить песню в альбом
DELETE	/api/v1/admin/albums/{album_id}/tracks/{song_id}/	Убрать песню из альбома
PATCH	/api/v1/admin/albums/{album_id}/tracks/{song_id}/	Изменить порядковый номер
POST /api/v1/admin/albums/{album_id}/tracks/

Тело запроса:

json
{
  "song_id": 102,
  "track_number": 4
}
Ответ 201:

json
{
  "data": {
    "album_id": 10,
    "song_id": 102,
    "track_number": 4,
    "created_at": "2025-01-15T12:00:00Z"
  }
}
PATCH /api/v1/admin/albums/{album_id}/tracks/{song_id}/

Тело запроса:

json
{
  "track_number": 5
}
Ответ 200:

json
{
  "data": {
    "album_id": 10,
    "song_id": 102,
    "track_number": 5,
    "created_at": "2025-01-15T12:00:00Z"
  }
}
Валидация:

song_id — обязательное, существующая песня

track_number — обязательное, положительное целое (> 0)

Песня не может быть дважды в одном альбоме (уникальность album_id + song_id)

track_number не может повторяться в рамках одного альбома (уникальность album_id + track_number)

Ошибка 400 (дубликат):

json
{
  "error": {
    "code": "validation_error",
    "message": "Эта песня уже есть в альбоме",
    "details": {
      "song_id": ["Песня уже добавлена в этот альбом"]
    }
  }
}
4. Пагинация
Для всех списков (публичных и админских):

Query Parameters:

Параметр	Тип	По умолчанию	Описание
page	int	1	Номер страницы
page_size	int	20	Размер страницы (макс. 100)
Формат meta:

json
{
  "meta": {
    "total": 150,
    "page": 2,
    "page_size": 20,
    "total_pages": 8
  }
}
5. CORS
Для разработки (localhost):

Access-Control-Allow-Origin: http://localhost:5174 (Vite dev server)

Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS

Access-Control-Allow-Headers: Content-Type, Authorization

6. Rate Limiting (базовое)
Для публичных эндпоинтов: 100 запросов/минуту на IP

Для админских: 300 запросов/минуту на сессию

7. Документация
Swagger: /api/docs/ (drf-yasg или drf-spectacular)

ReDoc: /api/redoc/