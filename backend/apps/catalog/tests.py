import json
import os
import tempfile
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from mutagen.id3 import APIC, ID3
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .admin import AlbumAdminForm, SongAdminForm
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


def make_mp3(name="track.mp3", duration_seconds=2, picture=None):
    header = bytes((0xFF, 0xFB, 0x90, 0x64))
    frame_len = 417
    frame = header + bytes(frame_len - 4)
    n_frames = max(1, round(duration_seconds * 44100 / 1152))
    payload = frame * n_frames

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(payload)
            tmp_path = tmp.name
        if picture is not None:
            tags = ID3()
            tags.add(
                APIC(
                    encoding=3,
                    mime="image/png",
                    type=3,
                    desc="Cover",
                    data=picture,
                )
            )
            tags.save(tmp_path)
        with open(tmp_path, "rb") as handle:
            content = handle.read()
    finally:
        if tmp_path:
            os.unlink(tmp_path)

    return SimpleUploadedFile(name, content, content_type="audio/mpeg")


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
        self.assertEqual(data["description"], "")
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

    def test_album_description_saved_and_public(self):
        artist = Artist.objects.create(name="Мот")
        text = "Дебютный альбом. Короткие песни про ночной город."
        create = self.client.post(
            "/api/v1/admin/albums/",
            {
                "title": "Ночной город",
                "artist_id": artist.id,
                "year": 2024,
                "description": f"  {text}  \r\n",
            },
            format="multipart",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data["data"]["description"], text)
        album_id = create.data["data"]["id"]

        too_long = self.client.patch(
            f"/api/v1/admin/albums/{album_id}/",
            {"description": "а" * 501},
            format="multipart",
        )
        self.assertEqual(too_long.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", too_long.data["error"]["details"])

        guest = self.client_class()
        detail = guest.get(f"/api/v1/albums/{album_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["data"]["description"], text)

    def test_album_admin_form_description_max_length(self):
        artist = Artist.objects.create(name="Мот")
        valid = AlbumAdminForm(
            data={
                "title": "Альбом",
                "artist": artist.id,
                "year": 2024,
                "description": "а" * 500,
            }
        )
        self.assertTrue(valid.is_valid(), valid.errors)
        album = valid.save()
        self.assertEqual(len(album.description), 500)

        too_long = AlbumAdminForm(
            data={
                "title": "Другой",
                "artist": artist.id,
                "description": "а" * 501,
            }
        )
        self.assertFalse(too_long.is_valid())
        self.assertIn("description", too_long.errors)

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
                "lyrics": "Куплет один\n\nПрипев",
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
        self.assertEqual(data["lyrics"], "Куплет один\n\nПрипев")
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

    def test_song_duration_extracted_from_mp3(self):
        create = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "Автодлина",
                "audio_file": make_mp3(duration_seconds=2),
            },
            format="multipart",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        duration = create.data["data"]["duration_seconds"]
        self.assertGreaterEqual(duration, 1)
        self.assertLess(duration, 10)

    def test_song_duration_required_when_undetectable(self):
        response = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "Без длительности",
                "audio_file": make_audio(),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration_seconds", response.data["error"]["details"])

    def test_song_cover_extracted_from_mp3_unless_uploaded(self):
        picture = make_image("embedded.png").read()
        auto = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "С обложкой из mp3",
                "audio_file": make_mp3(picture=picture),
            },
            format="multipart",
        )
        self.assertEqual(auto.status_code, status.HTTP_201_CREATED)
        self.assertTrue(auto.data["data"]["cover_url"])
        auto_id = auto.data["data"]["id"]

        override = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "Своя обложка",
                "audio_file": make_mp3(picture=picture),
                "cover": make_image("manual.png"),
            },
            format="multipart",
        )
        self.assertEqual(override.status_code, status.HTTP_201_CREATED)
        self.assertTrue(override.data["data"]["cover_url"])
        self.assertNotEqual(
            Song.objects.get(pk=auto_id).cover.name,
            Song.objects.get(pk=override.data["data"]["id"]).cover.name,
        )

    def test_song_lyrics_on_public_album(self):
        artist = Artist.objects.create(name="Мот")
        album = Album.objects.create(title="Лучшие хиты", artist=artist)
        create = self.client.post(
            "/api/v1/admin/songs/",
            {
                "title": "Капкан",
                "audio_file": make_audio(),
                "duration_seconds": 210,
                "lyrics": "Первый куплет\nстрока\n\nПрипев",
                "album_assignments": json.dumps(
                    [{"album_id": album.id, "track_number": 1}]
                ),
            },
            format="multipart",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)

        guest = self.client_class()
        detail = guest.get(f"/api/v1/albums/{album.id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["data"]["description"], "")
        track = detail.data["data"]["tracks"][0]
        self.assertEqual(track["lyrics"], "Первый куплет\nстрока\n\nПрипев")

    def test_song_admin_form_hides_duration_unless_needed(self):
        valid = SongAdminForm(
            data={"title": "Форма", "lyrics": "текст", "duration_seconds": 12},
            files={"audio_file": make_audio()},
        )
        self.assertTrue(valid.is_valid(), valid.errors)
        song = valid.save()
        self.assertEqual(song.duration_seconds, 12)
        self.assertEqual(song.lyrics, "текст")

        missing = SongAdminForm(
            data={"title": "Форма"},
            files={"audio_file": make_audio()},
        )
        self.assertFalse(missing.is_valid())
        self.assertIn("duration_seconds", missing.errors)

        auto = SongAdminForm(
            data={"title": "Авто"},
            files={"audio_file": make_mp3(duration_seconds=2)},
        )
        self.assertTrue(auto.is_valid(), auto.errors)
        self.assertGreaterEqual(auto.cleaned_data["duration_seconds"], 1)

    def test_album_not_found_for_tracks(self):
        response = self.client.post(
            "/api/v1/admin/albums/999/tracks/",
            {"song_id": 1, "track_number": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Альбом не найден")


class MediaRangeTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        override = override_settings(MEDIA_ROOT=self.tmp.name)
        override.enable()
        self.addCleanup(override.disable)

        self.payload = bytes(range(256)) * 20
        dest = Path(self.tmp.name) / "songs" / "audio" / "seek.mp3"
        dest.parent.mkdir(parents=True)
        dest.write_bytes(self.payload)

    def _body(self, response):
        if getattr(response, "streaming", False):
            return b"".join(response.streaming_content)
        return response.content

    def test_full_response_advertises_accept_ranges(self):
        response = self.client.get("/media/songs/audio/seek.mp3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        self.assertEqual(int(response["Content-Length"]), len(self.payload))
        self.assertEqual(self._body(response), self.payload)

    def test_range_returns_partial_content(self):
        response = self.client.get(
            "/media/songs/audio/seek.mp3",
            HTTP_RANGE="bytes=100-199",
        )
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertEqual(response["Content-Range"], f"bytes 100-199/{len(self.payload)}")
        self.assertEqual(int(response["Content-Length"]), 100)
        self.assertEqual(self._body(response), self.payload[100:200])

    def test_open_ended_range(self):
        response = self.client.get(
            "/media/songs/audio/seek.mp3",
            HTTP_RANGE="bytes=5000-",
        )
        self.assertEqual(response.status_code, 206)
        self.assertEqual(
            response["Content-Range"],
            f"bytes 5000-{len(self.payload) - 1}/{len(self.payload)}",
        )
        self.assertEqual(self._body(response), self.payload[5000:])

    def test_unsatisfiable_range(self):
        response = self.client.get(
            "/media/songs/audio/seek.mp3",
            HTTP_RANGE="bytes=99999-",
        )
        self.assertEqual(response.status_code, 416)
        self.assertEqual(response["Content-Range"], f"bytes */{len(self.payload)}")

    def test_missing_file(self):
        response = self.client.get("/media/songs/audio/missing.mp3")
        self.assertEqual(response.status_code, 404)
