from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    cover = models.ImageField(upload_to="albums/covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("artist", "title")]

    def __str__(self):
        return self.title


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Mood(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    audio_file = models.FileField(upload_to="songs/audio/")
    duration_seconds = models.IntegerField(default=0)
    cover = models.ImageField(upload_to="songs/covers/", null=True, blank=True)
    genres = models.ManyToManyField(Genre, through="SongGenre", blank=True)
    moods = models.ManyToManyField(Mood, through="SongMood", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class AlbumSong(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    track_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ("album", "song"),
            ("album", "track_number"),
        ]

    def __str__(self):
        return f"{self.track_number}. {self.song}"


class SongGenre(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("song", "genre")]

    def __str__(self):
        return f"{self.song} — {self.genre}"


class SongMood(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("song", "mood")]

    def __str__(self):
        return f"{self.song} — {self.mood}"
