from django.db.models import Count, Prefetch, Q
from django.http import Http404, JsonResponse
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Album, AlbumSong, Artist, Genre, Mood, Song
from .pagination import StandardPagination
from .serializers import (
    AlbumDetailSerializer,
    AlbumListSerializer,
    ArtistSerializer,
    CatalogTrackSerializer,
    GenreSerializer,
    MoodSerializer,
    SearchAlbumSerializer,
    SearchSongSerializer,
)


def api_root(request):
    return JsonResponse(
        {
            "data": {
                "name": "MusicMe API",
                "version": "v1",
                "status": "ok",
            }
        }
    )


def parse_optional_int(params, name):
    value = params.get(name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError({name: ["Ожидалось целое число"]})


class GenreListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GenreSerializer
    pagination_class = StandardPagination
    queryset = Genre.objects.all().order_by("id")


class MoodListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = MoodSerializer
    pagination_class = StandardPagination
    queryset = Mood.objects.all().order_by("id")


class ArtistListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArtistSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        params = self.request.query_params
        genre_id = parse_optional_int(params, "genre_id")
        mood_id = parse_optional_int(params, "mood_id")
        search = params.get("search")

        qs = Artist.objects.all()

        if genre_id is not None:
            qs = qs.filter(
                id__in=AlbumSong.objects.filter(song__genres__id=genre_id).values(
                    "album__artist_id"
                )
            )

        if mood_id is not None:
            qs = qs.filter(
                id__in=AlbumSong.objects.filter(song__moods__id=mood_id).values(
                    "album__artist_id"
                )
            )

        if search:
            qs = qs.filter(name__icontains=search)

        return qs.annotate(albums_count=Count("album", distinct=True)).order_by("id")


class AlbumListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AlbumListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        params = self.request.query_params
        artist_id = parse_optional_int(params, "artist_id")
        genre_id = parse_optional_int(params, "genre_id")
        mood_id = parse_optional_int(params, "mood_id")
        year_from = parse_optional_int(params, "year_from")
        year_to = parse_optional_int(params, "year_to")
        search = params.get("search")

        qs = Album.objects.select_related("artist")

        if artist_id is not None:
            qs = qs.filter(artist_id=artist_id)

        if genre_id is not None:
            qs = qs.filter(
                id__in=AlbumSong.objects.filter(song__genres__id=genre_id).values(
                    "album_id"
                )
            )

        if mood_id is not None:
            qs = qs.filter(
                id__in=AlbumSong.objects.filter(song__moods__id=mood_id).values(
                    "album_id"
                )
            )

        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(artist__name__icontains=search)
            )

        if year_from is not None:
            qs = qs.filter(year__gte=year_from)

        if year_to is not None:
            qs = qs.filter(year__lte=year_to)

        return qs.annotate(tracks_count=Count("albumsong", distinct=True)).order_by(
            "id"
        )


class TrackListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CatalogTrackSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        params = self.request.query_params
        artist_id = parse_optional_int(params, "artist_id")
        album_id = parse_optional_int(params, "album_id")
        genre_id = parse_optional_int(params, "genre_id")
        mood_id = parse_optional_int(params, "mood_id")

        qs = AlbumSong.objects.select_related("album__artist", "song").prefetch_related(
            "song__genres",
            "song__moods",
        )

        if album_id is not None:
            qs = qs.filter(album_id=album_id)
        if artist_id is not None:
            qs = qs.filter(album__artist_id=artist_id)
        if genre_id is not None:
            qs = qs.filter(song__genres__id=genre_id)
        if mood_id is not None:
            qs = qs.filter(song__moods__id=mood_id)

        return qs.distinct().order_by("album_id", "track_number", "id")


class AlbumDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = AlbumDetailSerializer
    pagination_class = None

    def get_queryset(self):
        return Album.objects.select_related("artist").prefetch_related(
            Prefetch(
                "albumsong_set",
                queryset=AlbumSong.objects.select_related("song")
                .prefetch_related("song__genres", "song__moods")
                .order_by("track_number"),
            )
        )

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Альбом не найден")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("query")
        if query is None or len(query.strip()) < 2:
            return Response(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Поисковый запрос должен содержать минимум 2 символа",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = query.strip()

        artists = ArtistSerializer(
            Artist.objects.filter(name__icontains=query)
            .annotate(albums_count=Count("album", distinct=True))
            .order_by("id"),
            many=True,
        ).data

        albums = SearchAlbumSerializer(
            Album.objects.select_related("artist")
            .filter(title__icontains=query)
            .order_by("id"),
            many=True,
        ).data

        songs = SearchSongSerializer(
            Song.objects.filter(title__icontains=query)
            .prefetch_related(
                Prefetch(
                    "albumsong_set",
                    queryset=AlbumSong.objects.select_related("album__artist").order_by(
                        "album_id"
                    ),
                )
            )
            .order_by("id"),
            many=True,
        ).data

        return Response(
            {
                "data": {
                    "artists": artists,
                    "albums": albums,
                    "songs": songs,
                },
                "meta": {
                    "total_artists": len(artists),
                    "total_albums": len(albums),
                    "total_songs": len(songs),
                },
            }
        )
