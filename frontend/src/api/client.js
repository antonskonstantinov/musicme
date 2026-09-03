import axios from "axios";

import { showToast } from "../ui/toasts.js";

const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 15000,
});

async function retryFailedRequest(config) {
  const { useCatalogStore } = await import("../stores/catalog.js");
  const catalog = useCatalogStore();
  const url = String(config?.url || "");
  const params = config?.params || {};

  if (!catalog.initialAlbumLoaded) {
    return catalog.loadInitialContent();
  }
  if (url.includes("/search/")) {
    return catalog.search(params.query);
  }
  if (url.includes("/tracks/")) {
    return catalog.fetchTracks();
  }
  if (/\/albums\/\d+/.test(url)) {
    const albumId = Number(url.match(/\/albums\/(\d+)/)[1]);
    return catalog.fetchAlbumDetail(albumId);
  }
  if (url.includes("/albums/")) {
    return catalog.fetchAlbums(params.artist_id, params.genre_id, params.mood_id);
  }
  if (url.includes("/artists/")) {
    return catalog.fetchArtists(params.genre_id, params.mood_id);
  }
  if (url.includes("/genres/")) {
    return catalog.fetchGenres();
  }
  if (url.includes("/moods/")) {
    return catalog.fetchMoods();
  }
  return catalog.loadInitialContent();
}

apiClient.interceptors.response.use(
  (response) => {
    const payload = response.data;
    if (payload && typeof payload === "object" && "data" in payload) {
      return payload.data;
    }
    return payload;
  },
  (error) => {
    const apiMessage = error.response?.data?.error?.message;
    const isTimeout =
      error.code === "ECONNABORTED" ||
      String(error.message || "").toLowerCase().includes("timeout");
    const isNetwork = !error.response;

    let message = apiMessage || error.message;
    if (isNetwork || isTimeout) {
      message = "Не удалось загрузить данные";
    }

    console.error(message);

    showToast({
      message,
      retry: isTimeout ? () => retryFailedRequest(error.config) : null,
    });

    return Promise.reject(new Error(message));
  },
);

export default apiClient;
