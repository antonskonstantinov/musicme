<script setup>
import { computed } from "vue";

import { usePlayerStore } from "../../stores/player.js";

const props = defineProps({
  album: {
    type: Object,
    required: true,
  },
  showBack: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["back"]);
const player = usePlayerStore();

const artistName = computed(
  () => props.album.artist?.name || props.album.artist_name || "",
);

function formatDuration(seconds) {
  const total = Math.floor(Number(seconds) || 0);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function playTrack(track) {
  player.playTrack(track, props.album.tracks ?? []);
}
</script>

<template>
  <div>
    <button
      v-if="showBack"
      type="button"
      class="mb-4 text-sm text-gray-300 hover:text-white"
      @click="emit('back')"
    >
      Назад
    </button>

    <div class="mb-6 flex gap-4">
      <img
        v-if="album.cover_url"
        :src="album.cover_url"
        :alt="album.title"
        class="h-40 w-40 shrink-0 rounded-lg object-cover"
      />
      <div
        v-else
        class="h-40 w-40 shrink-0 rounded-lg bg-gray-800"
      />
      <div class="min-w-0">
        <h2 class="text-2xl font-bold text-white">{{ album.title }}</h2>
        <p class="mt-1 text-gray-300">{{ artistName }}</p>
        <p class="text-gray-400">{{ album.year }}</p>
      </div>
    </div>

    <ul class="divide-y divide-gray-800">
      <li
        v-for="track in album.tracks ?? []"
        :key="track.id"
        class="flex cursor-pointer items-center gap-3 py-3 hover:bg-gray-900"
        @click="playTrack(track)"
      >
        <span class="w-8 shrink-0 text-center text-sm text-gray-500">
          {{ track.track_number }}
        </span>
        <div class="min-w-0 flex-1">
          <p class="truncate font-medium text-white">{{ track.title }}</p>
          <div class="mt-1 flex flex-wrap gap-1">
            <span
              v-for="genre in track.genres ?? []"
              :key="`g-${genre.id}`"
              class="rounded-full bg-gray-800 px-2 py-0.5 text-xs text-gray-300"
            >
              {{ genre.name }}
            </span>
            <span
              v-for="mood in track.moods ?? []"
              :key="`m-${mood.id}`"
              class="rounded-full bg-gray-800 px-2 py-0.5 text-xs text-gray-400"
            >
              {{ mood.name }}
            </span>
          </div>
        </div>
        <span class="shrink-0 text-sm text-gray-400">
          {{ formatDuration(track.duration_seconds) }}
        </span>
        <button
          type="button"
          class="shrink-0 rounded-full bg-white px-3 py-1 text-sm font-medium text-gray-900 hover:bg-gray-200"
          @click.stop="playTrack(track)"
        >
          Play
        </button>
      </li>
    </ul>
  </div>
</template>
