from django.contrib import admin
from django.utils.html import format_html

from .models import Album, AlbumSong, Artist, Genre, Mood, Song, SongGenre, SongMood


class AlbumSongInline(admin.TabularInline):
    model = AlbumSong


class SongGenreInline(admin.TabularInline):
    model = SongGenre


class SongMoodInline(admin.TabularInline):
    model = SongMood


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "year", "cover_preview")
    search_fields = ("title",)
    inlines = [AlbumSongInline]

    @admin.display(description="Обложка")
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" alt="" style="height: 40px;" />',
                obj.cover.url,
            )
        return ""


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_seconds", "cover_preview")
    search_fields = ("title",)
    inlines = [SongGenreInline, SongMoodInline]

    @admin.display(description="Обложка")
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" alt="" style="height: 40px;" />',
                obj.cover.url,
            )
        return ""


@admin.register(AlbumSong)
class AlbumSongAdmin(admin.ModelAdmin):
    list_display = ("album", "song", "track_number")
    search_fields = ("album__title", "song__title")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
