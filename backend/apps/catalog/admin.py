from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.utils.html import format_html

from .audio_metadata import extract_audio_metadata
from .models import Album, AlbumSong, Artist, Genre, Mood, Song, SongGenre, SongMood


class AlbumSongInline(admin.TabularInline):
    model = AlbumSong


class SongGenreInline(admin.TabularInline):
    model = SongGenre


class SongMoodInline(admin.TabularInline):
    model = SongMood


class SongAdminForm(forms.ModelForm):
    duration_seconds = forms.IntegerField(
        required=False,
        min_value=0,
        label="Продолжительность (сек.)",
        help_text=(
            "Заполняется автоматически из аудиофайла. "
            "Укажите вручную, только если определить не удалось."
        ),
    )

    class Meta:
        model = Song
        fields = ("title", "audio_file", "lyrics", "cover", "duration_seconds")
        widgets = {
            "lyrics": forms.Textarea(
                attrs={
                    "rows": 14,
                    "cols": 80,
                    "placeholder": "Текст песни (необязательно)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extracted_cover = None
        if "lyrics" in self.fields:
            self.fields["lyrics"].required = False
            self.fields["lyrics"].help_text = (
                "Необязательно. Текст будет доступен на сайте."
            )

    def clean(self):
        cleaned = super().clean()
        audio = cleaned.get("audio_file")
        is_new_audio = isinstance(audio, UploadedFile)
        extracted = {"duration_seconds": None, "cover": None}
        if is_new_audio:
            extracted = extract_audio_metadata(audio)
        self.extracted_cover = extracted.get("cover")

        duration = extracted.get("duration_seconds")
        manual = cleaned.get("duration_seconds")
        if duration:
            cleaned["duration_seconds"] = duration
        elif manual is not None:
            cleaned["duration_seconds"] = manual
        elif self.instance.pk and self.instance.duration_seconds:
            cleaned["duration_seconds"] = self.instance.duration_seconds
        else:
            self.add_error(
                "duration_seconds",
                "Не удалось определить продолжительность из файла. "
                "Укажите её вручную (в секундах).",
            )
        return cleaned

    def save(self, commit=True):
        song = super().save(commit=False)
        user_cover = isinstance(self.cleaned_data.get("cover"), UploadedFile)
        if not user_cover and self.extracted_cover and not song.cover:
            song.cover = self.extracted_cover
        if commit:
            song.save()
            self.save_m2m()
        return song


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class AlbumAdminForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ("title", "artist", "year", "cover", "description")
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 6,
                    "cols": 80,
                    "maxlength": 500,
                    "placeholder": "Краткое описание альбома (необязательно)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "description" in self.fields:
            self.fields["description"].required = False
            self.fields["description"].help_text = (
                "Необязательно. До 500 символов. Показывается на странице альбома."
            )


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm
    list_display = ("title", "artist", "year", "cover_preview", "has_description")
    search_fields = ("title",)
    inlines = [AlbumSongInline]

    @admin.display(boolean=True, description="Описание")
    def has_description(self, obj):
        return bool((obj.description or "").strip())

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
    form = SongAdminForm
    list_display = ("title", "duration_seconds", "cover_preview", "has_lyrics")
    search_fields = ("title",)
    inlines = [SongGenreInline, SongMoodInline]

    def get_fieldsets(self, request, obj=None):
        main = (
            None,
            {"fields": ("title", "audio_file", "lyrics", "cover")},
        )
        duration = (
            "Продолжительность",
            {
                "fields": ("duration_seconds",),
                "description": (
                    "Обычно определяется автоматически из MP3. "
                    "Это поле нужно, только если длительность прочитать не удалось."
                ),
            },
        )
        if request.method == "POST" or (obj is not None and not obj.duration_seconds):
            return (main, duration)
        return (main,)

    @admin.display(description="Обложка")
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" alt="" style="height: 40px;" />',
                obj.cover.url,
            )
        return ""

    @admin.display(boolean=True, description="Текст")
    def has_lyrics(self, obj):
        return bool((obj.lyrics or "").strip())


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
