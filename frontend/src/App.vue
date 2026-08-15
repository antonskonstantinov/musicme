<script setup>
import { onMounted, ref } from "vue";

import { fetchApiRoot } from "./api/client.js";

const apiStatus = ref("loading");
const apiData = ref(null);
const apiError = ref(null);

onMounted(async () => {
  try {
    apiData.value = await fetchApiRoot();
    apiStatus.value = "ok";
  } catch (error) {
    apiStatus.value = "error";
    apiError.value = error.message;
  }
});
</script>

<template>
  <main class="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
    <h1 class="text-4xl font-bold tracking-tight">Muzzzic</h1>
    <p class="text-gray-400">Музыкальный каталог — этап 1</p>

    <section class="w-full max-w-md rounded-lg border border-gray-800 bg-gray-900 p-6">
      <h2 class="mb-3 text-lg font-semibold">Проверка API через Vite proxy</h2>

      <p v-if="apiStatus === 'loading'" class="text-gray-400">Загрузка...</p>

      <p v-else-if="apiStatus === 'error'" class="text-red-400">
        Ошибка: {{ apiError }}
      </p>

      <pre
        v-else
        class="overflow-x-auto rounded bg-gray-950 p-4 text-sm text-green-400"
      >{{ JSON.stringify(apiData, null, 2) }}</pre>
    </section>
  </main>
</template>
