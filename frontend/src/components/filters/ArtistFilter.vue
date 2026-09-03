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

watch(
  () => [filters.selectedGenre?.id ?? null, filters.selectedMood?.id ?? null],
  () => {
    loading.value = true;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      const id = ++requestId;
      try {
        await catalog.fetchArtists(
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
    :items="catalog.artists"
    :selected-id="filters.selectedArtist?.id ?? null"
    title="Артист"
    :loading="loading"
    empty-text="Нет артистов с такими параметрами"
    @select="filters.setArtist"
    @clear="filters.clearArtist"
  >
    <template #default="{ item }">
      <span class="flex max-w-[10rem] items-baseline gap-1.5">
        <span class="truncate font-medium">{{ item.name }}</span>
        <span class="shrink-0 text-[11px] text-gray-400">
          {{ formatAlbumsCount(item.albums_count) }}
        </span>
      </span>
    </template>
  </FilterCarousel>
</template>
