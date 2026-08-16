<script setup>
import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";
import FilterCarousel from "./FilterCarousel.vue";

const catalog = useCatalogStore();
const filters = useFiltersStore();
</script>

<template>
  <FilterCarousel
    :items="catalog.genres"
    :selected-id="filters.selectedGenre?.id ?? null"
    title="Жанр"
    empty-text="Жанры не добавлены"
    @select="filters.setGenre"
    @clear="filters.clearGenre"
  />
</template>
