 # DATA MODEL — MusicMe

1. Общие принципы
- **PK:** Все первичные ключи — `id` (BigAutoField)
- **Аудит:** Все таблицы содержат `created_at` и `updated_at` (auto_now_add / auto_now), кроме промежуточных таблиц M2M (только `created_at`)
- **Soft Delete:** Не используется, удаление — физическое (для простоты MVP)
- **Нейминг в БД:** snake_case (стандарт Django)
- **Каскадное удаление:** CASCADE для всех FK

2. ERD Диаграмма (Crow's Foot Notation)

```mermaid
erDiagram
    ARTIST ||--o{ ALBUM : "создаёт (1:N)"
    ALBUM ||--o{ ALBUM_SONG : "содержит (1:N)"
    SONG ||--o{ ALBUM_SONG : "входит в (1:N)"
    SONG ||--o{ SONG_GENRE : "имеет (1:N)"
    GENRE ||--o{ SONG_GENRE : "классифицирует (1:N)"
    SONG ||--o{ SONG_MOOD : "имеет (1:N)"
    MOOD ||--o{ SONG_MOOD : "описывает (1:N)"

    ARTIST {
        bigint id PK
        varchar(200) name UK "NOT NULL"
        datetime created_at "auto"
        datetime updated_at "auto"
    }

    ALBUM {
        bigint id PK
        varchar(200) title "NOT NULL"
        bigint artist_id FK "NOT NULL"
        int year "NULL"
        varchar cover_url "NULL"
        varchar(500) description "NULL / blank"
        datetime created_at "auto"
        datetime updated_at "auto"
        constraint unique_artist_title "UNIQUE(artist_id, title)"
    }

    SONG {
        bigint id PK
        varchar(200) title "NOT NULL"
        varchar audio_url "NOT NULL"
        int duration_seconds "NOT NULL DEFAULT 0"
        text lyrics "NULL / blank"
        varchar minus_url "NULL"
        varchar cover_url "NULL"
        datetime created_at "auto"
        datetime updated_at "auto"
    }

    ALBUM_SONG {
        bigint id PK
        bigint album_id FK "NOT NULL"
        bigint song_id FK "NOT NULL"
        int track_number "NOT NULL"
        datetime created_at "auto"
        constraint unique_album_song "UNIQUE(album_id, song_id)"
        constraint unique_album_track "UNIQUE(album_id, track_number)"
    }

    GENRE {
        bigint id PK
        varchar(100) name UK "NOT NULL"
        datetime created_at "auto"
    }

    SONG_GENRE {
        bigint id PK
        bigint song_id FK "NOT NULL"
        bigint genre_id FK "NOT NULL"
        constraint unique_song_genre "UNIQUE(song_id, genre_id)"
    }

    MOOD {
        bigint id PK
        varchar(100) name UK "NOT NULL"
        datetime created_at "auto"
    }

    SONG_MOOD {
        bigint id PK
        bigint song_id FK "NOT NULL"
        bigint mood_id FK "NOT NULL"
        constraint unique_song_mood "UNIQUE(song_id, mood_id)"
    }

3. Визуальное представление связей (ASCII)

┌─────────────┐         ┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   ARTIST    │ 1     N │    ALBUM    │ 1     N │  ALBUM_SONG  │ N     1 │     SONG    │
├─────────────┤─────────├─────────────┤─────────├──────────────┤─────────├─────────────┤
│ id (PK)     │         │ id (PK)     │         │ id (PK)      │         │ id (PK)     │
│ name (UK)   │         │ title       │         │ album_id (FK)│         │ title       │
│ created_at  │         │ year        │         │ song_id (FK) │         │ audio_url   │
│ updated_at  │         │ cover_url   │         │ track_number │         │ duration    │
└─────────────┘         │ description │         │ created_at   │         │ cover_url   │
                        │ artist_id   │         └──────────────┘         │ created_at  │
                        │ created_at  │                                  │ updated_at  │
                        │ updated_at  │                                  └─────────────┘
                        └─────────────┘
                                                                           │         │
                                                                           │         │
                                                                     M:N   │         │   M:N
                                                                           │         │
                                                              ┌────────────┘         └────────────┐
                                                              ▼                                       ▼
                                                     ┌──────────────┐                        ┌──────────────┐
                                                     │  SONG_GENRE  │                        │  SONG_MOOD   │
                                                     ├──────────────┤                        ├──────────────┤
                                                     │ id (PK)      │                        │ id (PK)      │
                                                     │ song_id (FK) │                        │ song_id (FK) │
                                                     │ genre_id(FK) │                        │ mood_id (FK) │
                                                     └──────────────┘                        └──────────────┘
                                                              │                                       │
                                                              │                                       │
                                                              ▼                                       ▼
                                                     ┌──────────────┐                        ┌──────────────┐
                                                     │    GENRE     │                        │     MOOD     │
                                                     ├──────────────┤                        ├──────────────┤
                                                     │ id (PK)      │                        │ id (PK)      │
                                                     │ name (UK)    │                        │ name (UK)    │
                                                     │ created_at   │                        │ created_at   │
                                                     └──────────────┘                        └──────────────┘

4. Описание связей
Связь	Нотация	Тип	Обязательность	Описание
Artist → Album	ARTIST ||---o{ ALBUM	1 : N	Альбом обязан иметь артиста	Один артист — много альбомов
Album → AlbumSong	ALBUM ||---o{ ALBUM_SONG	1 : N	Запись обязана иметь альбом	Один альбом — много записей
Song → AlbumSong	SONG ||---o{ ALBUM_SONG	1 : N	Запись обязана иметь песню	Одна песня — много записей
Album → Song	через ALBUM_SONG	N : N	Обе стороны опциональны	Песня может быть в разных альбомах
Song → Genre	через SONG_GENRE	N : N	Обе стороны опциональны	Песня может иметь несколько жанров
Song → Mood	через SONG_MOOD	N : N	Обе стороны опциональны	Песня может иметь несколько настроений
5. Сущности
5.1. ARTIST (Исполнитель)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
name	CharField(200)	UNIQUE, NOT NULL	Имя исполнителя
created_at	DateTimeField	auto_now_add	Дата создания
updated_at	DateTimeField	auto_now	Дата обновления
Индексы: name (UNIQUE)

5.2. ALBUM (Альбом)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
title	CharField(200)	NOT NULL	Название альбома
artist	ForeignKey(Artist)	NOT NULL, CASCADE	Владелец альбома
year	IntegerField	NULL, BLANK	Год выпуска (может быть неизвестен)
cover	ImageField	NULL, BLANK	Файл обложки (`upload_to=albums/covers/`, URL `/media/albums/covers/…`)
description	TextField(500)	BLANK, DEFAULT ''	Краткое описание альбома (необязательно, показывается на сайте)
created_at	DateTimeField	auto_now_add	Дата создания
updated_at	DateTimeField	auto_now	Дата обновления
Индексы: artist (FK), year
Уникальные ограничения: unique_together(artist, title) — у одного исполнителя не может быть двух альбомов с одинаковым названием

5.3. SONG (Песня)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
title	CharField(200)	NOT NULL	Название песни
audio_file	FileField	NOT NULL	Аудиофайл (mp3/wav/flac/ogg; `upload_to=songs/audio/`, URL `/media/songs/audio/…`)
duration_seconds	IntegerField	NOT NULL, DEFAULT 0	Длительность в секундах (из файла при загрузке; вручную — только если не удалось определить)
cover	ImageField	NULL, BLANK	Обложка песни (`upload_to=songs/covers/`; из ID3 APIC при загрузке mp3 либо файл из админки; fallback на фронте — обложка альбома)
lyrics	TextField	BLANK, DEFAULT ''	Текст песни (необязательно, показывается на сайте)
minus_file	FileField	NULL, BLANK	Минусовка (mp3/wav/flac/ogg; `upload_to=songs/minus/`, URL `/media/songs/minus/…`). Если загружена — на сайте кнопка «Минус»
genres	M2M(Genre)	BLANK	Жанры песни
moods	M2M(Mood)	BLANK	Настроения песни
created_at	DateTimeField	auto_now_add	Дата создания
updated_at	DateTimeField	auto_now	Дата обновления
Индексы: title
Примечание: Связь с Album — только через ALBUM_SONG

5.4. ALBUM_SONG (Связь Альбом ↔ Песня)
ВНИМАНИЕ: Явная промежуточная таблица M2M. Одна и та же песня может входить в разные альбомы с разными порядковыми номерами.

Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
album	ForeignKey(Album)	NOT NULL, CASCADE	Альбом
song	ForeignKey(Song)	NOT NULL, CASCADE	Песня
track_number	PositiveIntegerField	NOT NULL	Порядковый номер в альбоме
created_at	DateTimeField	auto_now_add	Дата создания
Индексы: album (FK), song (FK), (album, track_number)
Уникальные ограничения:

unique_together(album, song) — песня не может дважды входить в один альбом

unique_together(album, track_number) — номер трека в альбоме уникален

5.5. GENRE (Жанр)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
name	CharField(100)	UNIQUE, NOT NULL	Название жанра
created_at	DateTimeField	auto_now_add	Дата создания
Связь с Song: M2M через SONG_GENRE

5.6. MOOD (Настроение)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
name	CharField(100)	UNIQUE, NOT NULL	Название настроения
created_at	DateTimeField	auto_now_add	Дата создания
Связь с Song: M2M через SONG_MOOD

5.7. SONG_GENRE (Промежуточная)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
song	ForeignKey(Song)	NOT NULL, CASCADE	Песня
genre	ForeignKey(Genre)	NOT NULL, CASCADE	Жанр
Уникальные ограничения: unique_together(song, genre)

5.8. SONG_MOOD (Промежуточная)
Поле	Тип	Ограничения	Описание
id	BigAutoField	PK	Идентификатор
song	ForeignKey(Song)	NOT NULL, CASCADE	Песня
mood	ForeignKey(Mood)	NOT NULL, CASCADE	Настроение
Уникальные ограничения: unique_together(song, mood)

6. Миграции
Порядок создания:

Artist

Album (FK на Artist)

Song

Genre, Mood

AlbumSong (M2M с промежуточной моделью)

M2M: Song.genres → SongGenre, Song.moods → SongMood

7. Валидация данных (Business Rules)
Правило	Уровень
Нельзя создать альбом с пустым названием	DRF Serializer
Нельзя создать песню без аудиофайла	DRF Serializer
Нельзя добавить одну песню в один альбом дважды	DB Constraint
Нельзя задать двум песням в альбоме одинаковый track_number	DB Constraint
У одного исполнителя не может быть двух альбомов с одинаковым названием	DB Constraint
Жанры и настроения создаются только админом (справочники)	Permissions
Файлы: аудио (mp3, wav, flac, ogg) / обложки (jpg, png, webp)	DRF Serializer
Максимальный размер аудиофайла: 20 MB	DRF Serializer
year может быть NULL (неизвестен)	DRF Serializer
Описание альбома — необязательно, до 500 символов	Django Admin / DRF
Длительность трека берётся из аудиофайла; вручную — только если не определилась	Django Admin / DRF
Обложка трека может быть извлечена из тегов mp3 (APIC)	Django Admin / DRF
8. Каскадное удаление (Cascade Behavior)
Действие	Результат
Удаление ARTIST	Каскадно удаляются все ALBUM этого артиста
Удаление ALBUM	Удаляются записи ALBUM_SONG (но не сами SONG)
Удаление SONG	Удаляются записи ALBUM_SONG, SONG_GENRE, SONG_MOOD
Удаление GENRE	Удаляются записи SONG_GENRE (жанр снимается с песен)
Удаление MOOD	Удаляются записи SONG_MOOD (настроение снимается с песен)