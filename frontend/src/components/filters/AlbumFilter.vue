<script setup>
import { onBeforeUnmount, ref, watch } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";
import FilterCarousel from "./FilterCarousel.vue";

const catalog = useCatalogStore();
const filters = useFiltersStore();

const loading = ref(false);
let debounceTimer = null;
let requestId = 0;

function onSelect(album) {
  filters.setAlbum(album);
  catalog.fetchAlbumDetail(album.id);
}

watch(
  () => [
    filters.selectedGenre?.id ?? null,
    filters.selectedMood?.id ?? null,
    filters.selectedArtist?.id ?? null,
  ],
  () => {
    loading.value = true;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      const id = ++requestId;
      try {
        await catalog.fetchAlbums(
          filters.selectedArtist?.id,
          filters.selectedGenre?.id,
          filters.selectedMood?.id,
        );
      } finally {
        if (id === requestId) {
          loading.value = false;
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
  <FilterCarousel
    :items="catalog.albums"
    :selected-id="filters.selectedAlbum?.id ?? null"
    title="Альбом"
    :loading="loading"
    empty-text="Нет альбомов с такими параметрами"
    variant="tile"
    @select="onSelect"
    @clear="filters.clearAlbum"
  >
    <template #default="{ item }">
      <div class="flex w-14 flex-col items-center gap-1 sm:w-20">
        <img
          v-if="item.cover_url"
          :src="item.cover_url"
          :alt="item.title"
          loading="lazy"
          class="h-14 w-14 rounded-md object-cover sm:h-20 sm:w-20"
        />
        <div
          v-else
          class="h-14 w-14 rounded-md bg-gray-700 sm:h-20 sm:w-20"
        />
        <span class="w-full truncate text-center text-[11px] font-medium leading-tight sm:text-sm">
          {{ item.title }}
        </span>
        <span class="hidden text-[11px] text-gray-400 sm:block">{{ item.year }}</span>
      </div>
    </template>
  </FilterCarousel>
</template>
