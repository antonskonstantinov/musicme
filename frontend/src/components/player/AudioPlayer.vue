<script setup>
import { computed, ref, watch } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { usePlayerStore } from "../../stores/player.js";

const catalog = useCatalogStore();
const player = usePlayerStore();

const audio = ref(null);
const isLoading = ref(false);

const coverUrl = computed(
  () =>
    player.currentTrack?.cover_url || catalog.currentAlbum?.cover_url || "",
);

const subtitle = computed(() => {
  const track = player.currentTrack;
  const artist =
    track?.artist_name || catalog.currentAlbum?.artist?.name || "";
  const albumTitle = track?.album_title || catalog.currentAlbum?.title || "";
  return [artist, albumTitle].filter(Boolean).join(" — ");
});

const duration = computed(
  () => player.duration || player.currentTrack?.duration_seconds || 0,
);

function formatTime(seconds) {
  const total = Math.floor(Number(seconds) || 0);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

async function syncAudio() {
  const el = audio.value;
  const track = player.currentTrack;
  if (!el || !track?.audio_url) {
    return;
  }

  if (el.dataset.trackSrc !== track.audio_url) {
    el.dataset.trackSrc = track.audio_url;
    el.src = track.audio_url;
    isLoading.value = true;
    player.duration = track.duration_seconds || 0;
  }

  if (player.isPlaying) {
    try {
      await el.play();
    } catch {
      player.isPlaying = false;
    }
  } else {
    el.pause();
  }
}

function onTimeUpdate() {
  if (!audio.value) {
    return;
  }
  player.currentTime = audio.value.currentTime;
}

function onLoadedMetadata() {
  if (!audio.value) {
    return;
  }
  player.duration = audio.value.duration || player.duration;
  isLoading.value = false;
}

function onWaiting() {
  isLoading.value = true;
}

function onCanPlay() {
  isLoading.value = false;
}

function onError() {
  isLoading.value = false;
}

function onEnded() {
  player.next();
}

function onSeek(event) {
  const seconds = Number(event.target.value);
  player.seekTo(seconds);
  if (audio.value) {
    audio.value.currentTime = seconds;
  }
}

watch(
  () => [player.currentTrack, player.isPlaying],
  () => {
    syncAudio();
  },
);

watch(audio, () => {
  syncAudio();
});
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="player.currentTrack"
      class="fixed inset-x-0 bottom-0 z-40 border-t border-gray-800 bg-gray-900 px-4 py-3"
    >
    <audio
      ref="audio"
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @waiting="onWaiting"
      @canplay="onCanPlay"
      @error="onError"
      @ended="onEnded"
    />

    <div class="flex flex-wrap items-center gap-4">
      <img
        v-if="coverUrl"
        :src="coverUrl"
        :alt="player.currentTrack.title"
        class="h-12 w-12 rounded object-cover"
      />
      <div v-else class="h-12 w-12 rounded bg-gray-800" />

      <div class="min-w-0 flex-1">
        <p class="truncate font-medium text-white">
          {{ player.currentTrack.title }}
        </p>
        <p class="truncate text-sm text-gray-400">{{ subtitle }}</p>
      </div>

      <div
        v-if="isLoading"
        class="h-8 w-8 animate-spin rounded-full border-2 border-gray-600 border-t-white"
      />
      <button
        v-else
        type="button"
        class="rounded-full bg-white px-4 py-1.5 text-sm font-medium text-gray-900"
        @click="player.togglePlay"
      >
        {{ player.isPlaying ? "Pause" : "Play" }}
      </button>

      <button
        type="button"
        class="rounded-full border border-gray-600 px-4 py-1.5 text-sm text-gray-200"
        @click="player.stop"
      >
        Stop
      </button>

      <input
        type="range"
        min="0"
        :max="duration"
        step="0.1"
        :value="player.currentTime"
        class="h-1 min-w-[8rem] flex-1 accent-white"
        @input="onSeek"
      />

      <span class="shrink-0 text-xs tabular-nums text-gray-400">
        {{ formatTime(player.currentTime) }} / {{ formatTime(duration) }}
      </span>

      <button
        type="button"
        class="text-sm text-gray-400 hover:text-white"
        @click="player.stop"
      >
        Закрыть
      </button>
    </div>
    </div>
  </Transition>
</template>
