import json
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Album, AlbumSong, Artist, Genre, Mood, Song


def make_image(name="cover.png", image_format="PNG"):
    buffer = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(buffer, format=image_format)
    buffer.seek(0)
    content_type = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
    }[image_format]
    return SimpleUploadedFile(name, buffer.read(), content_type=content_type)


def make_audio(name="track.mp3", size=16):
    return SimpleUploadedFile(name, b"0" * size, content_type="audio/mpeg")


@override_settings(MEDIA_ROOT="/tmp/muzzzic-test-media")
class AdminAPITestCase(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username="admin",
            password="pass",
            is_staff=True,
        )
        self.user = user_model.objects.create_user(
            username="user",
            password="pass",
            is_staff=False,
        )
        self.client.force_authenticate(self.admin)

    def test_unauthenticated_gets_401(self):
        guest = self.client_class()
        response = guest.get("/api/v1/admin/artists/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"]["code"], "authentication_required")

    def test_non_admin_gets_403(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/admin/artists/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "permission_denied")

    def test_artist_crud(self):
        create = self.client.post(
            "/api/v1/admin/artists/",
            {"name": "Новый Артист"},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", create.data)
        self.assertNotIn("meta", create.data)
        artist_id = create.data["data"]["id"]
        self.assertEqual(create.data["data"]["name"], "Новый Артист")
        self.assertEqual(create.data["data"]["albums_count"], 0)
        self.assertIn("created_at", create.data["data"])
        self.assertIn("updated_at", create.data["data"])

        listing = self.client.get("/api/v1/admin/artists/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertIn("data", listing.data)
        self.assertIn("meta", listing.data)
        self.assertEqual(listing.data["meta"]["total"], 1)

        detail = self.client.get(f"/api/v1/admin/artists/{artist_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["data"]["id"], artist_id)

        patch = self.client.patch(
            f"/api/v1/admin/artists/{artist_id}/",
            {"name": "Мот"},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["data"]["name"], "Мот")

        delete = self.client.delete(f"/api/v1/admin/artists/{artist_id}/")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Artist.objects.count(), 0)

    def test_artist_name_unique_and_required(self):
        Artist.objects.create(name="Мот")
        duplicate = self.client.post(
            "/api/v1/admin/artists/",
            {"name": "Мот"},
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate.data["error"]["code"], "validation_error")

        empty = self.client.post(
            "/api/v1/admin/artists/",
            {"name": ""},
            format="json",
        )
        self.assertEqual(empty.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", empty.data["error"]["details"])

    def test_album_crud_with_cover(self):
        artist = Artist.objects.create(name="Мот")
        create = self.client.post(
            "/api/v1/admin/albums/",
            {
                "title": "Новый Альбом",
                "artist_id": artist.id,
                "year": 2024,
                "cover": make_image(),
            },
            format="multipart",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        data = create.data["data"]
        self.assertEqual(data["title"], "Новый Альбом")
        self.assertEqual(data["year"], 2024)
        self.assertEqual(data["artist"], {"id": artist.id, "name": "Мот"})
        self.assertTrue(data["cover_url"])
        album_id = data["id"]

        duplicate = self.client.post(
            "/api/v1/admin/albums/",
            {"title": "Новый Альбом", "artist_id": artist.id},
            format="multipart",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_year = self.client.post(
            "/api/v1/admin/albums/",
            {"title": "Другой", "artist_id": artist.id, "year": 1700},
            format="multipart",
        )
        self.assertEqual(invalid_year.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("year", invalid_year.data["error"]["details"])

        patch = self.client.patch(
            f"/api/v1/admin/albums/{album_id}/",
            {"year": 2025},
            format="multipart",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["data"]["year"], 2025)

        delete = self.client.delete(f"/api/v1/admin/albums/{album_id}/")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)

    def test_album_cover_rejects_gif_and_oversize(self):
        artist = Artist.objects.create(name="Мот")
        gif = SimpleUploadedFile("cover.gif", b"GIF89a", content_type="image/gif")
        response = self.client.post(
            "/api/v1/admin/albums/",
            {"title": "A", "artist_id": artist.id, "cover": gif},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        huge = SimpleUploadedFile(
            "cover.png",
            b"0" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        huge_response = self.client.post(
            "/api/v1/admin/albums/",
            {"title": "B", "artist_id": artist.id, "cover": huge},
            format="multipart",
        )
        self.assertEqual(huge_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_song_crud_with_assignments(self):
        artist = Artist.objects.create(name="Мот")
        album = Album.objects.create(title="Лучшие хиты", artist=artist, year=2023)
        genre = Genre.objects.create(name="Hip-Hop")
        mood = Mood.objects.create(name="Энергичное")

        create = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "Новая Песня",
                "audio_file": make_audio(),
                "duration_seconds": 215,
                "cover": make_image("song.png"),
                "genre_ids": json.dumps([genre.id]),
                "mood_ids": json.dumps([mood.id]),
                "album_assignments": json.dumps(
                    [{"album_id": album.id, "track_number": 3}]
                ),
            },
            format="multipart",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        data = create.data["data"]
        self.assertEqual(data["title"], "Новая Песня")
        self.assertEqual(data["duration_seconds"], 215)
        self.assertTrue(data["audio_url"])
        self.assertTrue(data["cover_url"])
        self.assertEqual(data["genres"], [{"id": genre.id, "name": "Hip-Hop"}])
        self.assertEqual(data["moods"], [{"id": mood.id, "name": "Энергичное"}])
        self.assertEqual(
            data["albums"],
            [{"album_id": album.id, "track_number": 3}],
        )
        song_id = data["id"]
        self.assertTrue(AlbumSong.objects.filter(album=album, song_id=song_id).exists())

        listing = self.client.get("/api/v1/admin/songs/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data["meta"]["total"], 1)

        patch = self.client.patch(
            f"/api/v1/admin/songs/{song_id}/",
            {"title": "Капкан"},
            format="multipart",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["data"]["title"], "Капкан")

        delete = self.client.delete(f"/api/v1/admin/songs/{song_id}/")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Song.objects.count(), 0)
        self.assertEqual(AlbumSong.objects.count(), 0)

    def test_song_validation(self):
        missing = self.client.post(
            "/api/v1/admin/songs/",
            {"duration_seconds": 10},
            format="multipart",
        )
        self.assertEqual(missing.status_code, status.HTTP_400_BAD_REQUEST)
        details = missing.data["error"]["details"]
        self.assertIn("title", details)
        self.assertIn("audio_file", details)

        bad_audio = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "X",
                "audio_file": make_audio("track.txt"),
                "duration_seconds": 10,
            },
            format="multipart",
        )
        self.assertEqual(bad_audio.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("audio_file", bad_audio.data["error"]["details"])

        negative = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "X",
                "audio_file": make_audio(),
                "duration_seconds": -1,
            },
            format="multipart",
        )
        self.assertEqual(negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration_seconds", negative.data["error"]["details"])

        huge_audio = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "X",
                "audio_file": make_audio(size=20 * 1024 * 1024 + 1),
                "duration_seconds": 10,
            },
            format="multipart",
        )
        self.assertEqual(huge_audio.status_code, status.HTTP_400_BAD_REQUEST)

    def test_song_cannot_be_assigned_twice_to_same_album(self):
        artist = Artist.objects.create(name="Мот")
        album = Album.objects.create(title="Лучшие хиты", artist=artist)
        response = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "Дубль",
                "audio_file": make_audio(),
                "duration_seconds": 10,
                "album_assignments": json.dumps(
                    [
                        {"album_id": album.id, "track_number": 1},
                        {"album_id": album.id, "track_number": 2},
                    ]
                ),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("album_assignments", response.data["error"]["details"])

    def test_genre_and_mood_crud(self):
        genre = self.client.post(
            "/api/v1/admin/genres/",
            {"name": "Lo-Fi"},
            format="json",
        )
        self.assertEqual(genre.status_code, status.HTTP_201_CREATED)
        self.assertEqual(genre.data["data"]["name"], "Lo-Fi")
        self.assertIn("created_at", genre.data["data"])
        genre_id = genre.data["data"]["id"]

        mood = self.client.post(
            "/api/v1/admin/moods/",
            {"name": "Задумчивое"},
            format="json",
        )
        self.assertEqual(mood.status_code, status.HTTP_201_CREATED)
        mood_id = mood.data["data"]["id"]

        listing = self.client.get("/api/v1/admin/genres/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data["meta"]["total"], 1)

        duplicate = self.client.post(
            "/api/v1/admin/genres/",
            {"name": "Lo-Fi"},
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            self.client.delete(f"/api/v1/admin/genres/{genre_id}/").status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(
            self.client.delete(f"/api/v1/admin/moods/{mood_id}/").status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_album_tracks_endpoints(self):
        artist = Artist.objects.create(name="Мот")
        album = Album.objects.create(title="Лучшие хиты", artist=artist)
        song = Song.objects.create(
            title="Капкан",
            audio_file=make_audio(),
            duration_seconds=210,
        )

        create = self.client.post(
            f"/api/v1/admin/albums/{album.id}/tracks/",
            {"song_id": song.id, "track_number": 4},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            create.data["data"],
            {
                "album_id": album.id,
                "song_id": song.id,
                "track_number": 4,
                "created_at": create.data["data"]["created_at"],
            },
        )

        duplicate = self.client.post(
            f"/api/v1/admin/albums/{album.id}/tracks/",
            {"song_id": song.id, "track_number": 5},
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate.data["error"]["message"], "Эта песня уже есть в альбоме")
        self.assertEqual(
            duplicate.data["error"]["details"]["song_id"],
            ["Песня уже добавлена в этот альбом"],
        )

        other = Song.objects.create(
            title="Соло",
            audio_file=make_audio("other.mp3"),
            duration_seconds=185,
        )
        track_conflict = self.client.post(
            f"/api/v1/admin/albums/{album.id}/tracks/",
            {"song_id": other.id, "track_number": 4},
            format="json",
        )
        self.assertEqual(track_conflict.status_code, status.HTTP_400_BAD_REQUEST)

        patch = self.client.patch(
            f"/api/v1/admin/albums/{album.id}/tracks/{song.id}/",
            {"track_number": 5},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["data"]["track_number"], 5)

        delete = self.client.delete(
            f"/api/v1/admin/albums/{album.id}/tracks/{song.id}/"
        )
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            AlbumSong.objects.filter(album=album, song=song).exists()
        )

    def test_album_not_found_for_tracks(self):
        response = self.client.post(
            "/api/v1/admin/albums/999/tracks/",
            {"song_id": 1, "track_number": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Альбом не найден")
