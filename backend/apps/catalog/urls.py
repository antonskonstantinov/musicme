from django.urls import path

from . import views

urlpatterns = [
    path("", views.api_root, name="api-root"),
    path("genres/", views.GenreListView.as_view(), name="genre-list"),
    path("moods/", views.MoodListView.as_view(), name="mood-list"),
    path("artists/", views.ArtistListView.as_view(), name="artist-list"),
    path("albums/", views.AlbumListView.as_view(), name="album-list"),
    path("albums/<int:pk>/", views.AlbumDetailView.as_view(), name="album-detail"),
    path("search/", views.SearchView.as_view(), name="search"),
]
