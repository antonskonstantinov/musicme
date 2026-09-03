<script setup>
import { computed } from "vue";

import { usePlayerStore } from "../../stores/player.js";

const props = defineProps({
  tracks: {
    type: Array,
    default: () => [],
  },
  album: {
    type: Object,
    default: null,
  },
  showNumbers: {
    type: Boolean,
    default: false,
  },
});

const player = usePlayerStore();

const artistName = computed(
  () => props.album?.artist?.name || props.album?.artist_name || "",
);

const albumDescription = computed(() =>
  String(props.album?.description || "").trim(),
);

function formatDuration(seconds) {
  const total = Math.floor(Number(seconds) || 0);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function hasLyrics(track) {
  return Boolean(String(track?.lyrics || "").trim());
}

function hasMinus(track) {
  return Boolean(track?.minus_url);
}

function coverUrl(track) {
  return track?.cover_url || track?.album_cover_url || props.album?.cover_url || "";
}

function trackSubtitle(track) {
  const parts = [
    track.artist_name,
    track.album_title,
  ].filter(Boolean);
  return parts.join(" — ");
}

function playTrack(track) {
  player.playTrack(track, props.tracks);
}

function showLyrics(track) {
  player.openLyrics(track);
}

function playMinus(track) {
  player.playMinus(track, props.tracks);
}

function isPlayingMinus(track) {
  return (
    player.isMinus &&
    player.currentTrack?.id === track.id &&
    (player.currentTrack?.album_id || null) === (track.album_id || null)
  );
}
</script>

<template>
  <div>
    <div
      v-if="album"
      class="mb-8 flex flex-col gap-5 sm:flex-row sm:items-start sm:gap-6"
    >
      <img
        v-if="album.cover_url"
        :src="album.cover_url"
        :alt="album.title"
        class="h-40 w-40 shrink-0 rounded-xl object-cover shadow-lg shadow-black/40 sm:h-44 sm:w-44"
      />
      <div
        v-else
        class="h-40 w-40 shrink-0 rounded-xl bg-gray-800 sm:h-44 sm:w-44"
      />
      <div class="min-w-0 flex-1">
        <h2 class="text-2xl font-bold tracking-tight text-white sm:text-3xl">
          {{ album.title }}
        </h2>
        <p class="mt-1 text-gray-300">{{ artistName }}</p>
        <p v-if="album.year" class="text-sm text-gray-500">{{ album.year }}</p>
        <div
          v-if="albumDescription"
          class="mt-4 max-w-xl border-l border-white/20 pl-4"
        >
          <p
            class="text-[11px] font-medium uppercase tracking-[0.16em] text-gray-500"
          >
            Об альбоме
          </p>
          <p
            class="mt-2 whitespace-pre-wrap text-[15px] leading-relaxed text-gray-300"
          >
            {{ albumDescription }}
          </p>
        </div>
      </div>
    </div>

    <ul class="divide-y divide-gray-800">
      <li
        v-for="track in tracks"
        :key="`${track.album_id || 'song'}-${track.id}`"
        class="flex cursor-pointer items-center gap-3 py-3 hover:bg-gray-900"
        @click="playTrack(track)"
      >
        <span
          v-if="showNumbers"
          class="w-8 shrink-0 text-center text-sm text-gray-500"
        >
          {{ track.track_number }}
        </span>
        <img
          v-if="coverUrl(track)"
          :src="coverUrl(track)"
          :alt="track.title"
          class="h-12 w-12 shrink-0 rounded object-cover"
        />
        <div v-else class="h-12 w-12 shrink-0 rounded bg-gray-800" />
        <div class="min-w-0 flex-1">
          <p class="truncate font-medium text-white">{{ track.title }}</p>
          <p
            v-if="trackSubtitle(track)"
            class="truncate text-sm text-gray-400"
          >
            {{ trackSubtitle(track) }}
          </p>
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
          v-if="hasLyrics(track)"
          type="button"
          class="shrink-0 rounded-full border border-gray-600 px-3 py-1 text-sm text-gray-200 hover:border-gray-400 hover:text-white"
          @click.stop="showLyrics(track)"
        >
          Текст
        </button>
        <button
          v-if="hasMinus(track)"
          type="button"
          class="shrink-0 rounded-full border px-3 py-1 text-sm"
          :class="
            isPlayingMinus(track)
              ? 'border-white text-white'
              : 'border-gray-600 text-gray-200 hover:border-gray-400 hover:text-white'
          "
          @click.stop="playMinus(track)"
        >
          Минус
        </button>
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
