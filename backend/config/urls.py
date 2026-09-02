from django.contrib import admin
from django.urls import include, path, re_path

from apps.catalog.media import serve_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.catalog.urls")),
    re_path(r"^media/(?P<path>.*)$", serve_media),
]
