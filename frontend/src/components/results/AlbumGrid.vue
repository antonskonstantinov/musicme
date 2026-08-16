<script setup>
import { computed, watch } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";
import { usePlayerStore } from "../../stores/player.js";
import Spinner from "../ui/Spinner.vue";
import AlbumCard from "./AlbumCard.vue";
import SearchResults from "./SearchResults.vue";
import TrackList from "./TrackList.vue";

const catalog = useCatalogStore();
const filters = useFiltersStore();
const player = usePlayerStore();

const viewMode = computed(() => {
  if (catalog.searchResults !== null && !filters.selectedAlbum) {
    return "search";
  }

  if (filters.selectedAlbum || filters.isDefaultState) {
    if (filters.isDefaultState && !catalog.albums.length && !catalog.currentAlbum) {
      return "empty-db";
    }
    return "tracks";
  }

  if (!catalog.albums.length) {
    return "empty-filters";
  }

  return "grid";
});

const trackAlbum = computed(() => {
  if (filters.selectedAlbum) {
    if (catalog.currentAlbum?.id === filters.selectedAlbum.id) {
      return catalog.currentAlbum;
    }
    return null;
  }
  if (filters.isDefaultState) {
    return catalog.currentAlbum;
  }
  return null;
});

function firstAlbum() {
  if (!catalog.albums.length) {
    return null;
  }
  return catalog.albums.reduce((min, album) =>
    album.id < min.id ? album : min,
  );
}

function setFirstTrackPaused() {
  const tracks = catalog.currentAlbum?.tracks ?? [];
  if (!tracks.length) {
    return;
  }
  player.currentTrack = tracks[0];
  player.queue = [...tracks];
  player.currentIndex = 0;
  player.isPlaying = false;
  player.currentTime = 0;
}

async function showFirstAlbum() {
  const album = firstAlbum();
  if (!album) {
    return;
  }
  if (catalog.currentAlbum?.id !== album.id) {
    await catalog.fetchAlbumDetail(album.id);
  }
  setFirstTrackPaused();
}

function onBack() {
  filters.clearAlbum();
}

watch(
  () => [filters.isDefaultState, catalog.albums],
  async ([isDefault]) => {
    if (!isDefault) {
      return;
    }
    await showFirstAlbum();
  },
);
</script>

<template>
  <section aria-label="Результаты" class="flex-1 px-4 py-6 pb-32">
    <Transition name="fade-mode" mode="out-in">
      <SearchResults v-if="viewMode === 'search'" key="search" />

      <p v-else-if="viewMode === 'empty-db'" key="empty-db" class="text-gray-400">
        Контент скоро появится
      </p>

      <p v-else-if="viewMode === 'empty-filters'" key="empty-filters" class="text-gray-400">
        Ничего не найдено. Измените параметры.
      </p>

      <Spinner
        v-else-if="viewMode === 'tracks' && !trackAlbum"
        key="tracks-loading"
        label="Загрузка"
      />

      <TrackList
        v-else-if="viewMode === 'tracks' && trackAlbum"
        :key="`tracks-${trackAlbum.id}`"
        :album="trackAlbum"
        :show-back="Boolean(filters.selectedAlbum)"
        @back="onBack"
      />

      <div
        v-else-if="viewMode === 'grid'"
        key="grid"
        class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6"
      >
        <AlbumCard
          v-for="album in catalog.albums"
          :key="album.id"
          :album="album"
        />
      </div>
    </Transition>
  </section>
</template>
