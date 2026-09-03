<script setup>
import { computed, onBeforeUnmount, watch } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";
import Spinner from "../ui/Spinner.vue";
import SearchResults from "./SearchResults.vue";
import TrackList from "./TrackList.vue";

const catalog = useCatalogStore();
const filters = useFiltersStore();

let debounceTimer = null;
let requestId = 0;

const viewMode = computed(() => {
  if (catalog.searchResults !== null && !filters.selectedAlbum) {
    return "search";
  }

  if (catalog.isTracksLoading && !catalog.tracks.length) {
    return "tracks-loading";
  }

  if (!catalog.tracks.length) {
    return filters.hasActiveFilters ? "empty-filters" : "empty-db";
  }

  return "tracks";
});

const headerAlbum = computed(() => {
  if (!filters.selectedAlbum) {
    return null;
  }
  if (catalog.currentAlbum?.id === filters.selectedAlbum.id) {
    return catalog.currentAlbum;
  }
  return filters.selectedAlbum;
});

watch(
  () => [
    filters.selectedGenre?.id ?? null,
    filters.selectedMood?.id ?? null,
    filters.selectedArtist?.id ?? null,
    filters.selectedAlbum?.id ?? null,
  ],
  () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      const id = ++requestId;
      try {
        await catalog.fetchTracks();
      } finally {
        if (id !== requestId) {
          return;
        }
      }
    }, 300);
  },
);

onBeforeUnmount(() => {
  clearTimeout(debounceTimer);
});
</script>

<template>
  <section aria-label="Результаты" class="flex-1 px-4 pb-32 pt-3 sm:pt-6">
    <Transition name="fade-mode" mode="out-in">
      <SearchResults v-if="viewMode === 'search'" key="search" />

      <p v-else-if="viewMode === 'empty-db'" key="empty-db" class="text-gray-400">
        Контент скоро появится
      </p>

      <p v-else-if="viewMode === 'empty-filters'" key="empty-filters" class="text-gray-400">
        Ничего не найдено. Измените параметры.
      </p>

      <Spinner
        v-else-if="viewMode === 'tracks-loading'"
        key="tracks-loading"
        label="Загрузка"
      />

      <TrackList
        v-else
        key="tracks"
        :tracks="catalog.tracks"
        :album="headerAlbum"
        :show-numbers="Boolean(filters.selectedAlbum)"
      />
    </Transition>
  </section>
</template>
