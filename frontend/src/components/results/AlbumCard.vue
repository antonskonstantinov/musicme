<script setup>
import { computed } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";

const props = defineProps({
  album: {
    type: Object,
    required: true,
  },
});

const catalog = useCatalogStore();
const filters = useFiltersStore();

const artistName = computed(
  () => props.album.artist?.name || props.album.artist_name || "",
);

async function onSelect() {
  filters.setAlbum(props.album);
  await catalog.fetchAlbumDetail(props.album.id);
}
</script>

<template>
  <button type="button" class="group w-full text-left" @click="onSelect">
    <div class="relative">
      <img
        v-if="album.cover_url"
        :src="album.cover_url"
        :alt="album.title"
        loading="lazy"
        class="aspect-square w-full rounded-lg object-cover transition group-hover:scale-[1.03] group-hover:shadow-lg"
      />
      <div
        v-else
        class="aspect-square w-full rounded-lg bg-gray-800 transition group-hover:scale-[1.03] group-hover:shadow-lg"
      />
      <span
        class="absolute right-2 top-2 rounded-full bg-black/70 px-2 py-0.5 text-xs text-white"
      >
        {{ album.tracks_count ?? 0 }}
      </span>
    </div>
    <p class="mt-2 truncate font-bold text-white">{{ album.title }}</p>
    <p class="truncate text-sm text-gray-400">{{ artistName }}</p>
    <p class="text-sm text-gray-400">{{ album.year }}</p>
  </button>
</template>
