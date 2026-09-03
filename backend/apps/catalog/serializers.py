import json

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from rest_framework import serializers

from .audio_metadata import extract_audio_metadata
from .exceptions import raise_api_validation_error
from .models import Album, AlbumSong, Artist, Genre, Mood, Song, SongGenre, SongMood
from .validators import validate_audio_file, validate_cover_file


def media_url(file_field):
    if file_field:
        return file_field.url
    return None


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ("id", "name")


class ArtistSerializer(serializers.ModelSerializer):
    albums_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Artist
        fields = ("id", "name", "albums_count")


class ArtistNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ("id", "name")


class AlbumListSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    artist = ArtistNestedSerializer(read_only=True)
    tracks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Album
        fields = ("id", "title", "year", "cover_url", "artist", "tracks_count")

    def get_cover_url(self, obj):
        return media_url(obj.cover)


class AlbumTrackSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="song.id")
    title = serializers.CharField(source="song.title")
    duration_seconds = serializers.IntegerField(source="song.duration_seconds")
    lyrics = serializers.CharField(source="song.lyrics")
    audio_url = serializers.SerializerMethodField()
    minus_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    genres = GenreSerializer(source="song.genres", many=True)
    moods = MoodSerializer(source="song.moods", many=True)

    class Meta:
        model = AlbumSong
        fields = (
            "id",
            "title",
            "track_number",
            "duration_seconds",
            "lyrics",
            "audio_url",
            "minus_url",
            "cover_url",
            "genres",
            "moods",
        )

    def get_audio_url(self, obj):
        return media_url(obj.song.audio_file)

    def get_minus_url(self, obj):
        return media_url(obj.song.minus_file)

    def get_cover_url(self, obj):
        return media_url(obj.song.cover)


class AlbumDetailSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    artist = ArtistNestedSerializer(read_only=True)
    tracks = AlbumTrackSerializer(source="albumsong_set", many=True, read_only=True)

    class Meta:
        model = Album
        fields = (
            "id",
            "title",
            "year",
            "cover_url",
            "description",
            "artist",
            "tracks",
        )

    def get_cover_url(self, obj):
        return media_url(obj.cover)


class SearchAlbumSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(source="artist.id")
    artist_name = serializers.CharField(source="artist.name")

    class Meta:
        model = Album
        fields = ("id", "title", "year", "cover_url", "artist_id", "artist_name")

    def get_cover_url(self, obj):
        return media_url(obj.cover)


class SearchSongSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    minus_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    album_id = serializers.SerializerMethodField()
    album_title = serializers.SerializerMethodField()
    album_cover_url = serializers.SerializerMethodField()
    artist_name = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "duration_seconds",
            "lyrics",
            "audio_url",
            "minus_url",
            "cover_url",
            "album_id",
            "album_title",
            "album_cover_url",
            "artist_name",
        )

    def _album_song(self, obj):
        album_songs = list(obj.albumsong_set.all())
        if not album_songs:
            return None
        return album_songs[0]

    def get_audio_url(self, obj):
        return media_url(obj.audio_file)

    def get_minus_url(self, obj):
        return media_url(obj.minus_file)

    def get_cover_url(self, obj):
        return media_url(obj.cover)

    def get_album_id(self, obj):
        album_song = self._album_song(obj)
        if album_song is None:
            return None
        return album_song.album_id

    def get_album_title(self, obj):
        album_song = self._album_song(obj)
        if album_song is None:
            return None
        return album_song.album.title

    def get_album_cover_url(self, obj):
        album_song = self._album_song(obj)
        if album_song is None:
            return None
        return media_url(album_song.album.cover)

    def get_artist_name(self, obj):
        album_song = self._album_song(obj)
        if album_song is None:
            return None
        return album_song.album.artist.name


class CatalogTrackSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="song.id")
    title = serializers.CharField(source="song.title")
    duration_seconds = serializers.IntegerField(source="song.duration_seconds")
    lyrics = serializers.CharField(source="song.lyrics")
    audio_url = serializers.SerializerMethodField()
    minus_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    album_id = serializers.IntegerField(source="album.id")
    album_title = serializers.CharField(source="album.title")
    album_cover_url = serializers.SerializerMethodField()
    artist_id = serializers.IntegerField(source="album.artist_id")
    artist_name = serializers.CharField(source="album.artist.name")
    genres = GenreSerializer(source="song.genres", many=True)
    moods = MoodSerializer(source="song.moods", many=True)

    class Meta:
        model = AlbumSong
        fields = (
            "id",
            "title",
            "track_number",
            "duration_seconds",
            "lyrics",
            "audio_url",
            "minus_url",
            "cover_url",
            "album_id",
            "album_title",
            "album_cover_url",
            "artist_id",
            "artist_name",
            "genres",
            "moods",
        )

    def get_audio_url(self, obj):
        return media_url(obj.song.audio_file)

    def get_minus_url(self, obj):
        return media_url(obj.song.minus_file)

    def get_cover_url(self, obj):
        return media_url(obj.song.cover)

    def get_album_cover_url(self, obj):
        return media_url(obj.album.cover)


class SongSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    minus_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)
    moods = MoodSerializer(many=True, read_only=True)

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "audio_url",
            "minus_url",
            "duration_seconds",
            "lyrics",
            "cover_url",
            "genres",
            "moods",
        )

    def get_audio_url(self, obj):
        return media_url(obj.audio_file)

    def get_minus_url(self, obj):
        return media_url(obj.minus_file)

    def get_cover_url(self, obj):
        return media_url(obj.cover)


class AlbumSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumSong
        fields = ("id", "album", "song", "track_number", "created_at")


class SongGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongGenre
        fields = ("id", "song", "genre")


class SongMoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongMood
        fields = ("id", "song", "mood")


def parse_list_input(data):
    if isinstance(data, str):
        stripped = data.strip()
        if stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Некорректный JSON-массив.")
        if stripped == "":
            return []
        return [data]
    if (
        isinstance(data, list)
        and len(data) == 1
        and isinstance(data[0], str)
        and data[0].strip().startswith("[")
    ):
        try:
            return json.loads(data[0])
        except json.JSONDecodeError:
            raise serializers.ValidationError("Некорректный JSON-массив.")
    return data


class JSONListField(serializers.ListField):
    def to_internal_value(self, data):
        return super().to_internal_value(parse_list_input(data))


class ExistingPKListField(JSONListField):
    def __init__(self, queryset, not_found_message, **kwargs):
        self.model_queryset = queryset
        self.not_found_message = not_found_message
        kwargs.setdefault("child", serializers.IntegerField(min_value=1))
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        ids = super().to_internal_value(data)
        existing = set(
            self.model_queryset.filter(pk__in=ids).values_list("pk", flat=True)
        )
        missing = [pk for pk in ids if pk not in existing]
        if missing:
            raise serializers.ValidationError(
                f"{self.not_found_message}: {missing}."
            )
        return ids


class AudioFileField(serializers.FileField):
    def to_internal_value(self, data):
        uploaded = super().to_internal_value(data)
        return validate_audio_file(uploaded)


class CoverImageField(serializers.ImageField):
    def to_internal_value(self, data):
        uploaded = super().to_internal_value(data)
        return validate_cover_file(uploaded)


class NullableYearField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class OptionalDurationField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class AdminArtistSerializer(serializers.ModelSerializer):
    albums_count = serializers.IntegerField(read_only=True, default=0)
    name = serializers.CharField(min_length=1, max_length=200)

    class Meta:
        model = Artist
        fields = ("id", "name", "albums_count", "created_at", "updated_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Это поле обязательно.")
        qs = Artist.objects.filter(name=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Исполнитель с таким именем уже существует."
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["albums_count"] = getattr(
            instance, "albums_count", instance.album_set.count()
        )
        return data


class AdminGenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=1, max_length=100)

    class Meta:
        model = Genre
        fields = ("id", "name", "created_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Это поле обязательно.")
        qs = Genre.objects.filter(name=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Жанр с таким названием уже существует.")
        return value


class AdminMoodSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=1, max_length=100)

    class Meta:
        model = Mood
        fields = ("id", "name", "created_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Это поле обязательно.")
        qs = Mood.objects.filter(name=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Настроение с таким названием уже существует."
            )
        return value


class AdminAlbumSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    artist = ArtistNestedSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source="artist",
        write_only=True,
        error_messages={
            "does_not_exist": "Артист не найден.",
            "incorrect_type": "Ожидался идентификатор артиста.",
        },
    )
    cover = CoverImageField(required=False, allow_null=True, write_only=True)
    title = serializers.CharField(min_length=1, max_length=200)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )
    year = NullableYearField(
        required=False,
        allow_null=True,
        min_value=1800,
        max_value=2100,
    )

    class Meta:
        model = Album
        fields = (
            "id",
            "title",
            "year",
            "description",
            "cover_url",
            "cover",
            "artist",
            "artist_id",
            "created_at",
            "updated_at",
        )

    def get_cover_url(self, obj):
        return media_url(obj.cover)

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Это поле обязательно.")
        return value

    def validate_description(self, value):
        return value.replace("\r\n", "\n").replace("\r", "\n").strip()

    def validate(self, attrs):
        artist = attrs.get("artist") or getattr(self.instance, "artist", None)
        title = attrs.get("title") or getattr(self.instance, "title", None)
        if artist is not None and title is not None:
            qs = Album.objects.filter(artist=artist, title=title)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "title": [
                            "У этого исполнителя уже есть альбом с таким названием."
                        ]
                    }
                )
        return attrs


class AlbumAssignmentSerializer(serializers.Serializer):
    album_id = serializers.IntegerField(min_value=1)
    track_number = serializers.IntegerField(min_value=1)

    def validate_album_id(self, value):
        if not Album.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Альбом не найден.")
        return value


class AlbumAssignmentListField(JSONListField):
    child = AlbumAssignmentSerializer()


class AdminSongSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    minus_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)
    moods = MoodSerializer(many=True, read_only=True)
    albums = serializers.SerializerMethodField()
    title = serializers.CharField(min_length=1, max_length=200)
    audio_file = AudioFileField(write_only=True)
    minus_file = AudioFileField(required=False, allow_null=True, write_only=True)
    cover = CoverImageField(required=False, allow_null=True, write_only=True)
    duration_seconds = OptionalDurationField(
        min_value=0,
        required=False,
        allow_null=True,
    )
    lyrics = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50000,
    )
    genre_ids = ExistingPKListField(
        queryset=Genre.objects.all(),
        not_found_message="Жанры не найдены",
        required=False,
        write_only=True,
    )
    mood_ids = ExistingPKListField(
        queryset=Mood.objects.all(),
        not_found_message="Настроения не найдены",
        required=False,
        write_only=True,
    )
    album_assignments = AlbumAssignmentListField(required=False, write_only=True)

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "duration_seconds",
            "lyrics",
            "audio_url",
            "minus_url",
            "cover_url",
            "audio_file",
            "minus_file",
            "cover",
            "genres",
            "moods",
            "albums",
            "genre_ids",
            "mood_ids",
            "album_assignments",
            "created_at",
            "updated_at",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._extracted_cover = None
        if self.instance is not None:
            self.fields["audio_file"].required = False
            if self.partial:
                self.fields["title"].required = False

    def get_audio_url(self, obj):
        return media_url(obj.audio_file)

    def get_minus_url(self, obj):
        return media_url(obj.minus_file)

    def get_cover_url(self, obj):
        return media_url(obj.cover)

    def get_albums(self, obj):
        relations = obj.albumsong_set.all()
        return [
            {"album_id": rel.album_id, "track_number": rel.track_number}
            for rel in relations
        ]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Это поле обязательно.")
        return value

    def validate_lyrics(self, value):
        return value.replace("\r\n", "\n").replace("\r", "\n")

    def validate(self, attrs):
        audio = attrs.get("audio_file")
        is_new_audio = isinstance(audio, UploadedFile)
        extracted_duration = None
        if is_new_audio:
            metadata = extract_audio_metadata(audio)
            extracted_duration = metadata.get("duration_seconds")
            self._extracted_cover = metadata.get("cover")

        if extracted_duration:
            attrs["duration_seconds"] = extracted_duration
        elif attrs.get("duration_seconds") is not None:
            pass
        elif self.instance is not None:
            attrs.pop("duration_seconds", None)
        else:
            raise serializers.ValidationError(
                {
                    "duration_seconds": (
                        "Не удалось определить продолжительность из файла. "
                        "Укажите её вручную."
                    )
                }
            )
        return attrs

    def validate_album_assignments(self, value):
        album_ids = [item["album_id"] for item in value]
        if len(album_ids) != len(set(album_ids)):
            raise serializers.ValidationError(
                "Песня не может быть дважды в одном альбоме."
            )

        song = self.instance
        for item in value:
            qs = AlbumSong.objects.filter(
                album_id=item["album_id"],
                track_number=item["track_number"],
            )
            if song is not None:
                qs = qs.exclude(song=song)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Номер трека {item['track_number']} уже используется в этом альбоме."
                )
        return value

    def _replace_album_assignments(self, song, assignments):
        AlbumSong.objects.filter(song=song).delete()
        AlbumSong.objects.bulk_create(
            [
                AlbumSong(
                    album_id=item["album_id"],
                    song=song,
                    track_number=item["track_number"],
                )
                for item in assignments
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        genre_ids = validated_data.pop("genre_ids", [])
        mood_ids = validated_data.pop("mood_ids", [])
        album_assignments = validated_data.pop("album_assignments", [])
        if not validated_data.get("cover") and self._extracted_cover:
            validated_data["cover"] = self._extracted_cover
        song = Song.objects.create(**validated_data)
        if genre_ids:
            song.genres.set(genre_ids)
        if mood_ids:
            song.moods.set(mood_ids)
        if album_assignments:
            self._replace_album_assignments(song, album_assignments)
        return song

    @transaction.atomic
    def update(self, instance, validated_data):
        genre_ids = validated_data.pop("genre_ids", serializers.empty)
        mood_ids = validated_data.pop("mood_ids", serializers.empty)
        album_assignments = validated_data.pop("album_assignments", serializers.empty)
        if (
            "cover" not in validated_data
            and self._extracted_cover
            and not instance.cover
        ):
            validated_data["cover"] = self._extracted_cover

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if genre_ids is not serializers.empty:
            instance.genres.set(genre_ids)
        if mood_ids is not serializers.empty:
            instance.moods.set(mood_ids)
        if album_assignments is not serializers.empty:
            self._replace_album_assignments(instance, album_assignments)
        return instance


class AdminAlbumTrackSerializer(serializers.ModelSerializer):
    album_id = serializers.IntegerField(read_only=True)
    song_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AlbumSong
        fields = ("album_id", "song_id", "track_number", "created_at")


class AdminAlbumTrackWriteSerializer(serializers.Serializer):
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(),
        source="song",
        error_messages={
            "does_not_exist": "Песня не найдена.",
            "incorrect_type": "Ожидался идентификатор песни.",
        },
    )
    track_number = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        album = self.context["album"]
        song = attrs["song"]
        track_number = attrs["track_number"]

        if AlbumSong.objects.filter(album=album, song=song).exists():
            raise_api_validation_error(
                "Эта песня уже есть в альбоме",
                {"song_id": ["Песня уже добавлена в этот альбом"]},
            )

        if AlbumSong.objects.filter(album=album, track_number=track_number).exists():
            raise serializers.ValidationError(
                {"track_number": ["Номер трека уже используется в этом альбоме."]}
            )
        return attrs

    def create(self, validated_data):
        return AlbumSong.objects.create(
            album=self.context["album"],
            song=validated_data["song"],
            track_number=validated_data["track_number"],
        )


class AdminAlbumTrackUpdateSerializer(serializers.Serializer):
    track_number = serializers.IntegerField(min_value=1)

    def validate_track_number(self, value):
        album = self.context["album"]
        instance = self.context["instance"]
        if (
            AlbumSong.objects.filter(album=album, track_number=value)
            .exclude(pk=instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "Номер трека уже используется в этом альбоме."
            )
        return value

    def update(self, instance, validated_data):
        instance.track_number = validated_data["track_number"]
        instance.save(update_fields=["track_number"])
        return instance
