<script setup>
import { dismissToast, toasts } from "../../ui/toasts.js";

async function onRetry(toast) {
  dismissToast(toast.id);
  try {
    await toast.retry?.();
  } catch {
    // повторный тост покажет перехватчик Axios
  }
}
</script>

<template>
  <div class="pointer-events-none fixed right-4 top-4 z-[60] flex w-[min(100%-2rem,24rem)] flex-col gap-2">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="pointer-events-auto rounded-xl border border-gray-700 bg-gray-900 p-4 shadow-xl"
    >
      <p class="text-sm text-white">{{ toast.message }}</p>
      <div class="mt-3 flex items-center gap-2">
        <button
          v-if="toast.retry"
          type="button"
          class="rounded-lg bg-white px-3 py-1.5 text-sm font-medium text-gray-900"
          @click="onRetry(toast)"
        >
          Повторить
        </button>
        <button
          type="button"
          class="rounded-lg px-3 py-1.5 text-sm text-gray-300 hover:text-white"
          @click="dismissToast(toast.id)"
        >
          Закрыть
        </button>
      </div>
    </div>
  </div>
</template>
