from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import admin_views, views

router = DefaultRouter()
router.register("admin/artists", admin_views.AdminArtistViewSet, basename="admin-artist")
router.register("admin/albums", admin_views.AdminAlbumViewSet, basename="admin-album")
router.register("admin/songs", admin_views.AdminSongViewSet, basename="admin-song")
router.register("admin/genres", admin_views.AdminGenreViewSet, basename="admin-genre")
router.register("admin/moods", admin_views.AdminMoodViewSet, basename="admin-mood")

urlpatterns = [
    path("", views.api_root, name="api-root"),
    path("genres/", views.GenreListView.as_view(), name="genre-list"),
    path("moods/", views.MoodListView.as_view(), name="mood-list"),
    path("artists/", views.ArtistListView.as_view(), name="artist-list"),
    path("albums/", views.AlbumListView.as_view(), name="album-list"),
    path("albums/<int:pk>/", views.AlbumDetailView.as_view(), name="album-detail"),
    path("search/", views.SearchView.as_view(), name="search"),
    path(
        "admin/albums/<int:album_id>/tracks/",
        admin_views.AlbumTrackCreateView.as_view(),
        name="admin-album-track-create",
    ),
    path(
        "admin/albums/<int:album_id>/tracks/<int:song_id>/",
        admin_views.AlbumTrackDetailView.as_view(),
        name="admin-album-track-detail",
    ),
    path("", include(router.urls)),
]
