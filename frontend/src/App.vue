<script setup>
import { onMounted } from "vue";

import HeaderBar from "./components/layout/HeaderBar.vue";
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
      <section aria-label="Жанр" />
      <section aria-label="Настроение" />
      <section aria-label="Артист" />
      <section aria-label="Альбом" />
      <section aria-label="Результаты" />
    </main>
  </div>
</template>
