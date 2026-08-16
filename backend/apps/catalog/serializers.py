from rest_framework import serializers

from .models import Album, AlbumSong, Artist, Genre, Mood, Song, SongGenre, SongMood


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
    audio_url = serializers.SerializerMethodField()
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
            "audio_url",
            "cover_url",
            "genres",
            "moods",
        )

    def get_audio_url(self, obj):
        return media_url(obj.song.audio_file)

    def get_cover_url(self, obj):
        return media_url(obj.song.cover)


class AlbumDetailSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    artist = ArtistNestedSerializer(read_only=True)
    tracks = AlbumTrackSerializer(source="albumsong_set", many=True, read_only=True)

    class Meta:
        model = Album
        fields = ("id", "title", "year", "cover_url", "artist", "tracks")

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
    album_id = serializers.SerializerMethodField()
    album_title = serializers.SerializerMethodField()
    artist_name = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "duration_seconds",
            "audio_url",
            "album_id",
            "album_title",
            "artist_name",
        )

    def _album_song(self, obj):
        album_songs = list(obj.albumsong_set.all())
        if not album_songs:
            return None
        return album_songs[0]

    def get_audio_url(self, obj):
        return media_url(obj.audio_file)

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

    def get_artist_name(self, obj):
        album_song = self._album_song(obj)
        if album_song is None:
            return None
        return album_song.album.artist.name


class SongSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)
    moods = MoodSerializer(many=True, read_only=True)

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "audio_url",
            "duration_seconds",
            "cover_url",
            "genres",
            "moods",
        )

    def get_audio_url(self, obj):
        return media_url(obj.audio_file)

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
