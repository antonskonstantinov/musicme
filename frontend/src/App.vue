<script setup>
import { onMounted } from "vue";

import AlbumFilter from "./components/filters/AlbumFilter.vue";
import ArtistFilter from "./components/filters/ArtistFilter.vue";
import GenreFilter from "./components/filters/GenreFilter.vue";
import MoodFilter from "./components/filters/MoodFilter.vue";
import HeaderBar from "./components/layout/HeaderBar.vue";
import FilterChips from "./components/ui/FilterChips.vue";
import Spinner from "./components/ui/Spinner.vue";
import { useCatalogStore } from "./stores/catalog.js";

const catalog = useCatalogStore();

onMounted(() => {
  catalog.loadInitialContent();
});
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <HeaderBar />

    <div
      v-if="catalog.isInitialLoad"
      class="flex flex-1 items-center justify-center"
    >
      <Spinner label="Загрузка" />
    </div>

    <main v-else class="flex flex-1 flex-col">
      <GenreFilter />
      <MoodFilter />
      <ArtistFilter />
      <AlbumFilter />
      <FilterChips />
      <section aria-label="Результаты" />
    </main>
  </div>
</template>
