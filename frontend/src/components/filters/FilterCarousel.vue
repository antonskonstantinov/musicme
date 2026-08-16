<script setup>
import { onBeforeUnmount, ref, watch } from "vue";

defineProps({
  items: {
    type: Array,
    required: true,
  },
  selectedId: {
    type: Number,
    default: null,
  },
  title: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: "",
  },
});

defineEmits(["select", "clear"]);

const scroller = ref(null);

function onWheel(event) {
  if (event.deltaY === 0) {
    return;
  }
  event.preventDefault();
  event.currentTarget.scrollLeft += event.deltaY;
}

watch(scroller, (el, prev) => {
  prev?.removeEventListener("wheel", onWheel);
  el?.addEventListener("wheel", onWheel, { passive: false });
});

onBeforeUnmount(() => {
  scroller.value?.removeEventListener("wheel", onWheel);
});
</script>

<template>
  <section class="fade-in border-b border-gray-800 py-4">
    <div class="mb-3 flex items-center gap-2 px-4">
      <h2 class="text-sm font-semibold uppercase tracking-wide text-gray-400">
        {{ title }}
      </h2>
      <button
        v-if="selectedId != null"
        type="button"
        class="rounded-full border border-gray-700 px-2 py-0.5 text-xs text-gray-300 hover:border-gray-500 hover:text-white"
        @click="$emit('clear')"
      >
        Очистить
      </button>
    </div>

    <div v-if="loading" class="flex gap-3 overflow-hidden px-4">
      <div
        v-for="index in 6"
        :key="index"
        class="h-24 min-w-[8.5rem] shrink-0 animate-pulse rounded-2xl bg-gray-800"
      />
    </div>

    <p
      v-else-if="items.length === 0"
      class="px-4 text-sm text-gray-500"
    >
      {{ emptyText }}
    </p>

    <div
      v-else
      ref="scroller"
      class="carousel-track flex touch-pan-x gap-3 overflow-x-auto px-4"
    >
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        class="snap-start shrink-0 rounded-2xl border px-4 py-3 text-left shadow-md transition duration-200 hover:-translate-y-0.5 hover:shadow-xl"
        :class="
          item.id === selectedId
            ? 'border-white bg-gray-700 text-white shadow-lg ring-2 ring-white'
            : 'border-gray-700 bg-gray-800 text-gray-200 hover:border-gray-500'
        "
        @click="$emit('select', item)"
      >
        <slot :item="item" :selected="item.id === selectedId">
          {{ item.name }}
        </slot>
      </button>
    </div>
  </section>
</template>
