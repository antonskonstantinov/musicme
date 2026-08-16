<script setup>
import { computed } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";
import { usePlayerStore } from "../../stores/player.js";

const catalog = useCatalogStore();
const filters = useFiltersStore();
const player = usePlayerStore();

const results = computed(() => catalog.searchResults ?? { artists: [], albums: [], songs: [] });

const isEmpty = computed(() => {
  const data = results.value;
  return (
    !(data.artists ?? []).length &&
    !(data.albums ?? []).length &&
    !(data.songs ?? []).length
  );
});

function formatAlbumsCount(count) {
  const n = Number(count) || 0;
  const mod100 = n % 100;
  const mod10 = n % 10;
  if (mod100 >= 11 && mod100 <= 14) {
    return `${n} альбомов`;
  }
  if (mod10 === 1) {
    return `${n} альбом`;
  }
  if (mod10 >= 2 && mod10 <= 4) {
    return `${n} альбома`;
  }
  return `${n} альбомов`;
}

function selectArtist(artist) {
  filters.setArtist(artist);
}

async function openAlbum(album) {
  filters.setAlbum(album);
  await catalog.fetchAlbumDetail(album.id);
}

function playSong(song) {
  player.playTrack(song, results.value.songs ?? []);
}
</script>

<template>
  <div>
    <p v-if="isEmpty" class="text-gray-400">
      По запросу '{{ filters.searchQuery }}' ничего не найдено
    </p>

    <div v-else class="space-y-8">
      <section v-if="results.artists?.length">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
          Артисты
        </h2>
        <ul class="space-y-2">
          <li v-for="artist in results.artists" :key="artist.id">
            <button
              type="button"
              class="w-full rounded-lg px-3 py-2 text-left hover:bg-gray-900"
              @click="selectArtist(artist)"
            >
              <span class="font-medium text-white">{{ artist.name }}</span>
              <span class="ml-2 text-sm text-gray-400">
                {{ formatAlbumsCount(artist.albums_count) }}
              </span>
            </button>
          </li>
        </ul>
      </section>

      <section v-if="results.albums?.length">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
          Альбомы
        </h2>
        <ul class="space-y-2">
          <li v-for="album in results.albums" :key="album.id">
            <button
              type="button"
              class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left hover:bg-gray-900"
              @click="openAlbum(album)"
            >
              <img
                v-if="album.cover_url"
                :src="album.cover_url"
                :alt="album.title"
                loading="lazy"
                class="h-12 w-12 rounded object-cover"
              />
              <div v-else class="h-12 w-12 rounded bg-gray-800" />
              <div class="min-w-0">
                <p class="truncate font-medium text-white">{{ album.title }}</p>
                <p class="truncate text-sm text-gray-400">{{ album.artist_name }}</p>
              </div>
            </button>
          </li>
        </ul>
      </section>

      <section v-if="results.songs?.length">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
          Треки
        </h2>
        <ul class="space-y-2">
          <li v-for="song in results.songs" :key="song.id">
            <button
              type="button"
              class="w-full rounded-lg px-3 py-2 text-left hover:bg-gray-900"
              @click="playSong(song)"
            >
              <p class="truncate font-medium text-white">{{ song.title }}</p>
              <p class="truncate text-sm text-gray-400">
                {{ song.artist_name }} — {{ song.album_title }}
              </p>
            </button>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>
