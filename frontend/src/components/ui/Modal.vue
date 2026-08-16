<script setup>
defineEmits(["close"]);
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
    @click.self="$emit('close')"
  >
    <div class="w-full max-w-sm rounded-xl border border-gray-700 bg-gray-900 p-6 shadow-xl">
      <p class="text-center text-lg text-white">
        <slot />
      </p>
      <button
        type="button"
        class="mt-6 w-full rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-200 hover:bg-gray-700"
        @click="$emit('close')"
      >
        Закрыть
      </button>
    </div>
  </div>
</template>
