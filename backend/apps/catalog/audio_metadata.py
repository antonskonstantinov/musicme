import os
from io import BytesIO
from uuid import uuid4

import mutagen
from django.core.files.base import ContentFile
from mutagen.id3 import APIC
from PIL import Image, UnidentifiedImageError

from .validators import COVER_EXTENSIONS, COVER_MAX_BYTES

MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
PIL_FORMAT_TO_EXT = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


def extract_audio_metadata(uploaded_file):
    """Read duration and the first usable embedded cover from an audio upload."""
    audio = _open_mutagen(uploaded_file)
    return {
        "duration_seconds": _duration_seconds(audio),
        "cover": _embedded_cover(audio),
    }


def _open_mutagen(uploaded_file):
    path = getattr(uploaded_file, "path", None)
    if path and os.path.exists(path):
        try:
            return mutagen.File(path)
        except Exception:
            return None

    fileobj = getattr(uploaded_file, "file", uploaded_file)
    name = getattr(uploaded_file, "name", None) or getattr(fileobj, "name", None)
    try:
        if hasattr(fileobj, "seek"):
            fileobj.seek(0)
        audio = mutagen.File(fileobj, filename=name)
        if hasattr(fileobj, "seek"):
            fileobj.seek(0)
        return audio
    except Exception:
        if hasattr(fileobj, "seek"):
            try:
                fileobj.seek(0)
            except Exception:
                pass
        return None


def _duration_seconds(audio):
    info = getattr(audio, "info", None)
    length = getattr(info, "length", None) if info is not None else None
    try:
        length = float(length)
    except (TypeError, ValueError):
        return None
    if length <= 0:
        return None
    return max(1, int(round(length)))


def _embedded_cover(audio):
    if audio is None:
        return None
    for picture in _iter_pictures(audio):
        cover = _picture_to_content_file(picture)
        if cover is not None:
            return cover
    return None


def _iter_pictures(audio):
    pictures = []
    tags = getattr(audio, "tags", None)
    if tags is not None:
        getall = getattr(tags, "getall", None)
        if callable(getall):
            pictures.extend(getall("APIC"))
        else:
            try:
                for key in list(tags):
                    frame = tags[key]
                    if isinstance(frame, APIC) or str(key).startswith("APIC"):
                        pictures.append(frame)
            except Exception:
                pass

    pictures.extend(list(getattr(audio, "pictures", None) or []))

    def sort_key(picture):
        pic_type = getattr(picture, "type", None)
        try:
            pic_type = int(pic_type)
        except (TypeError, ValueError):
            pic_type = None
        return 0 if pic_type == 3 else 1

    pictures.sort(key=sort_key)
    return pictures


def _picture_to_content_file(picture):
    data = getattr(picture, "data", None)
    if not data:
        return None
    if len(data) > COVER_MAX_BYTES:
        return None

    mime = (getattr(picture, "mime", None) or "").split(";")[0].strip().lower()
    ext = MIME_TO_EXT.get(mime)
    if ext is None:
        ext = _sniff_image_ext(data)
    if ext not in COVER_EXTENSIONS and ext != ".jpeg":
        return None
    if ext == ".jpeg":
        ext = ".jpg"

    return ContentFile(data, name=f"embedded-{uuid4().hex[:8]}{ext}")


def _sniff_image_ext(data):
    try:
        with Image.open(BytesIO(data)) as image:
            return PIL_FORMAT_TO_EXT.get((image.format or "").upper())
    except (UnidentifiedImageError, OSError, ValueError):
        return None
