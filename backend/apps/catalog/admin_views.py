from django.db.models import Count, Prefetch
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Album, AlbumSong, Artist, Genre, Mood, Song
from .pagination import StandardPagination
from .serializers import (
    AdminAlbumSerializer,
    AdminAlbumTrackSerializer,
    AdminAlbumTrackUpdateSerializer,
    AdminAlbumTrackWriteSerializer,
    AdminArtistSerializer,
    AdminGenreSerializer,
    AdminMoodSerializer,
    AdminSongSerializer,
)


class WrappedModelMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({"data": self.get_serializer(instance).data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NamedNotFoundMixin:
    not_found_message = "Ресурс не найден"

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail=self.not_found_message)


class AdminArtistViewSet(WrappedModelMixin, NamedNotFoundMixin, ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminArtistSerializer
    pagination_class = StandardPagination
    not_found_message = "Исполнитель не найден"

    def get_queryset(self):
        return Artist.objects.annotate(
            albums_count=Count("album", distinct=True)
        ).order_by("id")


class AdminAlbumViewSet(WrappedModelMixin, NamedNotFoundMixin, ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminAlbumSerializer
    pagination_class = StandardPagination
    not_found_message = "Альбом не найден"

    def get_queryset(self):
        return Album.objects.select_related("artist").order_by("id")


class AdminSongViewSet(WrappedModelMixin, NamedNotFoundMixin, ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminSongSerializer
    pagination_class = StandardPagination
    not_found_message = "Песня не найдена"

    def get_queryset(self):
        return (
            Song.objects.prefetch_related(
                "genres",
                "moods",
                Prefetch(
                    "albumsong_set",
                    queryset=AlbumSong.objects.order_by("album_id", "track_number"),
                ),
            )
            .order_by("id")
        )


class AdminGenreViewSet(WrappedModelMixin, NamedNotFoundMixin, ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminGenreSerializer
    pagination_class = StandardPagination
    queryset = Genre.objects.all().order_by("id")
    not_found_message = "Жанр не найден"


class AdminMoodViewSet(WrappedModelMixin, NamedNotFoundMixin, ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminMoodSerializer
    pagination_class = StandardPagination
    queryset = Mood.objects.all().order_by("id")
    not_found_message = "Настроение не найдено"


def get_album_or_404(album_id):
    try:
        return Album.objects.get(pk=album_id)
    except Album.DoesNotExist:
        raise NotFound(detail="Альбом не найден")


class AlbumTrackCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, album_id):
        album = get_album_or_404(album_id)
        serializer = AdminAlbumTrackWriteSerializer(
            data=request.data,
            context={"album": album},
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {"data": AdminAlbumTrackSerializer(instance).data},
            status=status.HTTP_201_CREATED,
        )


class AlbumTrackDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_link(self, album_id, song_id):
        album = get_album_or_404(album_id)
        try:
            link = AlbumSong.objects.get(album=album, song_id=song_id)
        except AlbumSong.DoesNotExist:
            raise NotFound(detail="Песня не найдена в альбоме")
        return album, link

    def patch(self, request, album_id, song_id):
        album, link = self._get_link(album_id, song_id)
        serializer = AdminAlbumTrackUpdateSerializer(
            link,
            data=request.data,
            context={"album": album, "instance": link},
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({"data": AdminAlbumTrackSerializer(instance).data})

    def delete(self, request, album_id, song_id):
        _, link = self._get_link(album_id, song_id)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
