<script setup>
import { computed, onBeforeUnmount, onMounted } from "vue";

const props = defineProps({
  track: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close"]);

const verses = computed(() => {
  const text = String(props.track?.lyrics || "")
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .trim();
  if (!text) {
    return [];
  }
  return text.split(/\n{2,}/);
});

function onKeydown(event) {
  if (event.key === "Escape") {
    emit("close");
  }
}

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-end justify-center bg-black/70 sm:items-center sm:p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="lyrics-title"
    @click.self="emit('close')"
  >
    <div
      class="flex max-h-[85vh] w-full max-w-lg flex-col rounded-t-2xl border border-gray-700 bg-gray-900 shadow-2xl sm:rounded-2xl"
    >
      <header
        class="flex shrink-0 items-start justify-between gap-3 border-b border-gray-800 px-5 py-4"
      >
        <div class="min-w-0">
          <p class="text-xs uppercase tracking-wide text-gray-500">Текст песни</p>
          <h2
            id="lyrics-title"
            class="truncate text-lg font-semibold text-white"
          >
            {{ track.title }}
          </h2>
        </div>
        <button
          type="button"
          class="rounded-lg px-2 py-1 text-gray-400 hover:bg-gray-800 hover:text-white"
          aria-label="Закрыть"
          @click="emit('close')"
        >
          ✕
        </button>
      </header>

      <div class="overflow-y-auto px-5 py-8">
        <div
          class="mx-auto max-w-prose space-y-7 text-center"
        >
          <p
            v-for="(verse, index) in verses"
            :key="index"
            class="whitespace-pre-wrap text-[15px] leading-relaxed text-gray-200"
          >
            {{ verse }}
          </p>
          <p v-if="!verses.length" class="text-sm text-gray-500">
            Текст не указан
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
