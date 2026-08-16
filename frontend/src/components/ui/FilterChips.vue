<script setup>
import { useFiltersStore } from "../../stores/filters.js";

const filters = useFiltersStore();

const clearByType = {
  genre: filters.clearGenre,
  mood: filters.clearMood,
  artist: filters.clearArtist,
  album: filters.clearAlbum,
};

function clearFilter(type) {
  clearByType[type]?.();
}
</script>

<template>
  <section
    v-if="filters.hasActiveFilters"
    class="flex flex-wrap items-center gap-2 border-b border-gray-800 px-4 py-3"
  >
    <span
      v-for="chip in filters.activeFilters"
      :key="chip.type"
      class="inline-flex items-center gap-2 rounded-full border border-gray-700 bg-gray-800 px-3 py-1 text-sm text-gray-200"
    >
      {{ chip.label }}
      <button
        type="button"
        class="text-gray-400 hover:text-white"
        :aria-label="`Сбросить: ${chip.label}`"
        @click="clearFilter(chip.type)"
      >
        ×
      </button>
    </span>

    <button
      type="button"
      class="rounded-full border border-gray-600 px-3 py-1 text-sm text-gray-200 hover:border-white hover:text-white"
      @click="filters.resetAll"
    >
      Сбросить все
    </button>
  </section>
</template>
