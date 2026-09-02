"""Serve MEDIA files with HTTP Range so the HTML5 player can seek."""

from __future__ import annotations

import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseNotModified,
    StreamingHttpResponse,
)
from django.utils._os import safe_join
from django.utils.http import http_date
from django.views.static import was_modified_since

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
BLOCK_SIZE = 8192


class RangedFileReader:
    def __init__(self, fileobj, offset, length, block_size=BLOCK_SIZE):
        self.fileobj = fileobj
        self.remaining = length
        self.block_size = block_size
        fileobj.seek(offset)

    def __iter__(self):
        while self.remaining > 0:
            chunk = self.fileobj.read(min(self.block_size, self.remaining))
            if not chunk:
                break
            self.remaining -= len(chunk)
            yield chunk

    def close(self):
        self.fileobj.close()


def serve_media(request, path):
    if request.method not in ("GET", "HEAD"):
        return HttpResponse(status=405)

    document_root = Path(settings.MEDIA_ROOT)
    try:
        fullpath = Path(safe_join(str(document_root), path))
    except ValueError as exc:
        raise Http404() from exc

    if not fullpath.is_file():
        raise Http404()

    stat = fullpath.stat()
    if not was_modified_since(
        request.META.get("HTTP_IF_MODIFIED_SINCE"),
        stat.st_mtime,
    ):
        return HttpResponseNotModified()

    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    file_size = stat.st_size
    last_modified = http_date(stat.st_mtime)
    range_spec = _parse_range(request.META.get("HTTP_RANGE"), file_size)

    if range_spec == "unsatisfiable":
        response = HttpResponse(status=416)
        response["Content-Range"] = f"bytes */{file_size}"
        response["Accept-Ranges"] = "bytes"
        return response

    if range_spec:
        start, end = range_spec
        length = end - start + 1
        if request.method == "HEAD":
            response = HttpResponse(status=206, content_type=content_type)
        else:
            response = StreamingHttpResponse(
                RangedFileReader(fullpath.open("rb"), start, length),
                status=206,
                content_type=content_type,
            )
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response["Content-Length"] = str(length)
        _set_common_headers(response, last_modified, encoding)
        return response

    if request.method == "HEAD":
        response = HttpResponse(content_type=content_type)
        response["Content-Length"] = str(file_size)
    else:
        response = FileResponse(fullpath.open("rb"), content_type=content_type)
        response["Content-Length"] = str(file_size)
    _set_common_headers(response, last_modified, encoding)
    return response


def _set_common_headers(response, last_modified, encoding):
    response["Accept-Ranges"] = "bytes"
    response["Last-Modified"] = last_modified
    if encoding:
        response["Content-Encoding"] = encoding


def _parse_range(header, file_size):
    if not header:
        return None
    match = RANGE_RE.fullmatch(header.strip())
    if not match:
        return None
    start_s, end_s = match.groups()
    if not start_s and not end_s:
        return None
    if start_s:
        start = int(start_s)
        end = int(end_s) if end_s else file_size - 1
    else:
        suffix = int(end_s)
        if suffix == 0 or file_size == 0:
            return "unsatisfiable"
        start = max(file_size - suffix, 0)
        end = file_size - 1
    if file_size == 0 or start < 0 or start >= file_size or end < start:
        return "unsatisfiable"
    end = min(end, file_size - 1)
    return start, end
