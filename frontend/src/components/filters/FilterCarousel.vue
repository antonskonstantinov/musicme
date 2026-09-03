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
  variant: {
    type: String,
    default: "chip",
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
  <section class="fade-in border-b border-gray-800 py-1.5 sm:py-3">
    <div class="mb-1.5 flex items-center gap-2 px-4 sm:mb-2">
      <h2 class="text-[11px] font-semibold uppercase tracking-wide text-gray-400 sm:text-sm">
        {{ title }}
      </h2>
      <button
        v-if="selectedId != null"
        type="button"
        class="rounded-full border border-gray-700 px-2 py-0.5 text-[11px] text-gray-300 hover:border-gray-500 hover:text-white sm:text-xs"
        @click="$emit('clear')"
      >
        Очистить
      </button>
    </div>

    <div v-if="loading" class="flex gap-2 overflow-hidden px-4">
      <div
        v-for="index in 6"
        :key="index"
        class="shrink-0 animate-pulse rounded-xl bg-gray-800"
        :class="
          variant === 'tile'
            ? 'h-14 w-14 sm:h-20 sm:w-20'
            : 'h-8 min-w-[5.5rem]'
        "
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
      class="carousel-track flex touch-pan-x gap-2 overflow-x-auto px-4"
    >
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        class="snap-start shrink-0 border text-left transition duration-200"
        :class="[
          variant === 'tile'
            ? 'rounded-xl p-1 sm:p-1.5'
            : 'rounded-xl px-3 py-1.5 text-sm',
          item.id === selectedId
            ? 'border-white bg-gray-700 text-white ring-1 ring-white'
            : 'border-gray-700 bg-gray-800 text-gray-200 hover:border-gray-500',
        ]"
        @click="$emit('select', item)"
      >
        <slot :item="item" :selected="item.id === selectedId">
          {{ item.name }}
        </slot>
      </button>
    </div>
  </section>
</template>
