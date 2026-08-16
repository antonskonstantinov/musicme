from pathlib import Path

from rest_framework import serializers

AUDIO_MAX_BYTES = 20 * 1024 * 1024
COVER_MAX_BYTES = 5 * 1024 * 1024
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg"}
COVER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _file_extension(uploaded_file):
    name = getattr(uploaded_file, "name", "") or ""
    return Path(name).suffix.lower()


def validate_audio_file(uploaded_file):
    extension = _file_extension(uploaded_file)
    if extension not in AUDIO_EXTENSIONS:
        raise serializers.ValidationError(
            "Допустимые форматы: mp3, wav, flac, ogg."
        )
    size = getattr(uploaded_file, "size", 0) or 0
    if size > AUDIO_MAX_BYTES:
        raise serializers.ValidationError("Максимальный размер аудиофайла — 20 MB.")
    return uploaded_file


def validate_cover_file(uploaded_file):
    extension = _file_extension(uploaded_file)
    if extension not in COVER_EXTENSIONS:
        raise serializers.ValidationError(
            "Допустимые форматы обложки: jpg, png, webp."
        )
    size = getattr(uploaded_file, "size", 0) or 0
    if size > COVER_MAX_BYTES:
        raise serializers.ValidationError("Максимальный размер обложки — 5 MB.")
    return uploaded_file
