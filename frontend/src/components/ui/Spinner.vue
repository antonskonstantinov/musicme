<script setup>
defineProps({
  label: {
    type: String,
    default: "Загрузка",
  },
});
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3" role="status" :aria-label="label">
    <div
      class="h-10 w-10 animate-spin rounded-full border-2 border-gray-700 border-t-white"
    />
    <span class="text-sm text-gray-400">{{ label }}...</span>
  </div>
</template>
