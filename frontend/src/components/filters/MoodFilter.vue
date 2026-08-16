<script setup>
import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";
import FilterCarousel from "./FilterCarousel.vue";

const catalog = useCatalogStore();
const filters = useFiltersStore();
</script>

<template>
  <FilterCarousel
    :items="catalog.moods"
    :selected-id="filters.selectedMood?.id ?? null"
    title="Настроение"
    empty-text="Настроения не добавлены"
    @select="filters.setMood"
    @clear="filters.clearMood"
  />
</template>
