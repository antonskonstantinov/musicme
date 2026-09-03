import { defineStore } from "pinia";
import { ref } from "vue";

import apiClient from "../api/client.js";
import { useFiltersStore } from "./filters.js";
import { usePlayerStore } from "./player.js";

export const useCatalogStore = defineStore("catalog", () => {
  const genres = ref([]);
  const moods = ref([]);
  const artists = ref([]);
  const albums = ref([]);
  const tracks = ref([]);
  const currentAlbum = ref(null);
  const searchResults = ref(null);
  const initialAlbumLoaded = ref(false);
  const isInitialLoad = ref(true);
  const isTracksLoading = ref(false);

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

  async function fetchTracks() {
    const filters = useFiltersStore();
    const params = { page_size: 20 };
    if (filters.selectedGenre?.id != null) {
      params.genre_id = filters.selectedGenre.id;
    }
    if (filters.selectedMood?.id != null) {
      params.mood_id = filters.selectedMood.id;
    }
    if (filters.selectedArtist?.id != null) {
      params.artist_id = filters.selectedArtist.id;
    }
    if (filters.selectedAlbum?.id != null) {
      params.album_id = filters.selectedAlbum.id;
    }
    isTracksLoading.value = true;
    try {
      tracks.value = await apiClient.get("/tracks/", { params });
    } finally {
      isTracksLoading.value = false;
    }
  }

  async function search(query) {
    searchResults.value = await apiClient.get("/search/", {
      params: { query },
    });
  }

  function clearSearch() {
    searchResults.value = null;
  }

  function seedPlayerIfIdle() {
    const player = usePlayerStore();
    if (player.currentTrack || !tracks.value.length) {
      return;
    }
    player.currentTrack = tracks.value[0];
    player.queue = [...tracks.value];
    player.currentIndex = 0;
    player.isPlaying = false;
    player.currentTime = 0;
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
        fetchTracks(),
      ]);
      seedPlayerIfIdle();
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
    tracks,
    currentAlbum,
    searchResults,
    initialAlbumLoaded,
    isInitialLoad,
    isTracksLoading,
    fetchGenres,
    fetchMoods,
    fetchArtists,
    fetchAlbums,
    fetchAlbumDetail,
    fetchTracks,
    search,
    clearSearch,
    loadInitialContent,
  };
});
