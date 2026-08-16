import { defineStore } from "pinia";
import { ref } from "vue";

import apiClient from "../api/client.js";
import { usePlayerStore } from "./player.js";

export const useCatalogStore = defineStore("catalog", () => {
  const genres = ref([]);
  const moods = ref([]);
  const artists = ref([]);
  const albums = ref([]);
  const currentAlbum = ref(null);
  const searchResults = ref(null);
  const initialAlbumLoaded = ref(false);
  const isInitialLoad = ref(true);

  async function fetchGenres() {
    genres.value = await apiClient.get("/genres/");
  }

  async function fetchMoods() {
    moods.value = await apiClient.get("/moods/");
  }

  async function fetchArtists(genreId, moodId) {
    const params = {};
    if (genreId != null) {
      params.genre_id = genreId;
    }
    if (moodId != null) {
      params.mood_id = moodId;
    }
    artists.value = await apiClient.get("/artists/", { params });
  }

  async function fetchAlbums(artistId, genreId, moodId) {
    const params = {};
    if (artistId != null) {
      params.artist_id = artistId;
    }
    if (genreId != null) {
      params.genre_id = genreId;
    }
    if (moodId != null) {
      params.mood_id = moodId;
    }
    albums.value = await apiClient.get("/albums/", { params });
  }

  async function fetchAlbumDetail(albumId) {
    currentAlbum.value = await apiClient.get(`/albums/${albumId}/`);
  }

  async function search(query) {
    searchResults.value = await apiClient.get("/search/", {
      params: { query },
    });
  }

  function clearSearch() {
    searchResults.value = null;
  }

  async function loadInitialContent() {
    isInitialLoad.value = true;
    initialAlbumLoaded.value = false;

    try {
      await Promise.all([
        fetchGenres(),
        fetchMoods(),
        fetchArtists(),
        fetchAlbums(),
      ]);

      if (!albums.value.length) {
        return;
      }

      const firstAlbum = albums.value.reduce((min, album) =>
        album.id < min.id ? album : min,
      );
      await fetchAlbumDetail(firstAlbum.id);

      const tracks = currentAlbum.value?.tracks ?? [];
      if (tracks.length) {
        const player = usePlayerStore();
        player.currentTrack = tracks[0];
        player.queue = [...tracks];
        player.currentIndex = 0;
        player.isPlaying = false;
        player.currentTime = 0;
      }

      initialAlbumLoaded.value = true;
    } catch {
      // сообщение об ошибке выводит перехватчик Axios
    } finally {
      isInitialLoad.value = false;
    }
  }

  return {
    genres,
    moods,
    artists,
    albums,
    currentAlbum,
    searchResults,
    initialAlbumLoaded,
    isInitialLoad,
    fetchGenres,
    fetchMoods,
    fetchArtists,
    fetchAlbums,
    fetchAlbumDetail,
    search,
    clearSearch,
    loadInitialContent,
  };
});
