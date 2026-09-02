<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { useCatalogStore } from "../../stores/catalog.js";
import { usePlayerStore } from "../../stores/player.js";

const SILENT_WAV =
  "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA";

const catalog = useCatalogStore();
const player = usePlayerStore();

const audioA = ref(null);
const audioB = ref(null);
const usingA = ref(true);
const isLoading = ref(false);
const primed = ref(false);
const isSeeking = ref(false);
const seekPreview = ref(0);
let lastPositionSec = -1;
let pendingSeekSec = null;

const coverUrl = computed(
  () =>
    player.currentTrack?.cover_url || catalog.currentAlbum?.cover_url || "",
);

const artistName = computed(() => {
  const track = player.currentTrack;
  return track?.artist_name || catalog.currentAlbum?.artist?.name || "";
});

const albumTitle = computed(() => {
  const track = player.currentTrack;
  return track?.album_title || catalog.currentAlbum?.title || "";
});

const subtitle = computed(() =>
  [artistName.value, albumTitle.value].filter(Boolean).join(" — "),
);

const duration = computed(() => {
  const fromPlayer = Number(player.duration);
  if (Number.isFinite(fromPlayer) && fromPlayer > 0) {
    return fromPlayer;
  }
  const fromTrack = Number(player.currentTrack?.duration_seconds);
  if (Number.isFinite(fromTrack) && fromTrack > 0) {
    return fromTrack;
  }
  return 0;
});

const sliderValue = computed(() =>
  isSeeking.value ? seekPreview.value : Number(player.currentTime) || 0,
);

function formatTime(seconds) {
  const total = Math.floor(Number(seconds) || 0);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function activeEl() {
  return usingA.value ? audioA.value : audioB.value;
}

function standbyEl() {
  return usingA.value ? audioB.value : audioA.value;
}

function isActiveTarget(target) {
  return Boolean(target) && target === activeEl();
}

function absoluteUrl(url) {
  if (!url) {
    return "";
  }
  try {
    return new URL(url, window.location.origin).href;
  } catch {
    return url;
  }
}

function assignSrc(el, url) {
  if (!el || !url) {
    return false;
  }
  if (el.dataset.trackSrc === url) {
    return false;
  }
  el.dataset.trackSrc = url;
  el.preload = "auto";
  el.src = url;
  el.load();
  return true;
}

let ignoreMediaEventsUntil = 0;

function unlockElement(el) {
  if (!el) {
    return;
  }
  const hadSrc = Boolean(el.dataset.trackSrc);
  if (!hadSrc) {
    el.src = SILENT_WAV;
  }
  el.muted = true;
  el.play().catch(() => {});
  el.pause();
  try {
    el.currentTime = 0;
  } catch {
    // Some browsers reject currentTime before metadata.
  }
  el.muted = false;
  if (!hadSrc) {
    el.removeAttribute("src");
    delete el.dataset.trackSrc;
    el.load();
  }
}

function primeElements() {
  if (primed.value) {
    return;
  }
  primed.value = true;
  ignoreMediaEventsUntil = Date.now() + 500;
  unlockElement(audioA.value);
  unlockElement(audioB.value);
}

function prepareStandby() {
  const nextTrack = player.peekNextTrack();
  const standby = standbyEl();
  const active = activeEl();
  if (!standby || !nextTrack?.audio_url) {
    return;
  }
  if (active?.dataset.trackSrc === nextTrack.audio_url) {
    return;
  }
  assignSrc(standby, nextTrack.audio_url);
}

function promoteStandbyIfReady(trackUrl) {
  const standby = standbyEl();
  if (!standby || standby.dataset.trackSrc !== trackUrl) {
    return false;
  }
  const outgoing = activeEl();
  usingA.value = !usingA.value;
  outgoing.pause();
  const incoming = activeEl();
  if (incoming.ended || incoming.currentTime > 0.05) {
    incoming.currentTime = 0;
  }
  return true;
}

async function syncAudio() {
  const track = player.currentTrack;
  let el = activeEl();
  if (!el || !track?.audio_url) {
    return;
  }

  if (el.dataset.trackSrc !== track.audio_url) {
    if (promoteStandbyIfReady(track.audio_url)) {
      el = activeEl();
      isLoading.value = false;
    } else {
      assignSrc(el, track.audio_url);
      isLoading.value = true;
      player.duration = track.duration_seconds || 0;
    }
  } else if (el.ended) {
    el.currentTime = 0;
  }

  prepareStandby();

  if (player.isPlaying) {
    primeElements();
    try {
      await el.play();
    } catch {
      player.isPlaying = false;
    }
  } else {
    el.pause();
  }

  updateMediaSession();
}

function clampSeek(seconds) {
  const value = Number(seconds);
  if (!Number.isFinite(value)) {
    return 0;
  }
  const total = Number(duration.value);
  if (Number.isFinite(total) && total > 0) {
    return Math.min(Math.max(0, value), total);
  }
  return Math.max(0, value);
}

function applySeek(seconds) {
  const next = clampSeek(seconds);
  pendingSeekSec = next;
  seekPreview.value = next;
  player.seekTo(next);
  const el = activeEl();
  if (el && el.readyState >= HTMLMediaElement.HAVE_METADATA) {
    try {
      el.currentTime = next;
    } catch {
      // Some browsers reject currentTime before they can seek.
    }
  }
  updatePositionState();
}

function onSeekStart() {
  isSeeking.value = true;
  seekPreview.value = sliderValue.value;
}

function onSeekInput(event) {
  const seconds = Number(event.target.value);
  if (!Number.isFinite(seconds)) {
    return;
  }
  seekPreview.value = seconds;
  applySeek(seconds);
}

function onSeekCommit(event) {
  const seconds = Number(event.target.value);
  if (Number.isFinite(seconds)) {
    applySeek(seconds);
  }
  isSeeking.value = false;
}

function shouldIgnoreTimeUpdate(current) {
  if (isSeeking.value) {
    return true;
  }
  if (pendingSeekSec == null) {
    return false;
  }
  if (Math.abs(current - pendingSeekSec) > 1) {
    return true;
  }
  pendingSeekSec = null;
  return false;
}

function onTimeUpdate(event) {
  if (!isActiveTarget(event.target)) {
    return;
  }
  if (shouldIgnoreTimeUpdate(event.target.currentTime)) {
    return;
  }
  player.currentTime = event.target.currentTime;
  const sec = Math.floor(event.target.currentTime || 0);
  if (sec !== lastPositionSec) {
    lastPositionSec = sec;
    updatePositionState();
  }
}

function onLoadedMetadata(event) {
  if (!isActiveTarget(event.target)) {
    return;
  }
  const loaded = Number(event.target.duration);
  if (Number.isFinite(loaded) && loaded > 0) {
    player.duration = loaded;
  }
  if (pendingSeekSec != null && event.target.readyState >= HTMLMediaElement.HAVE_METADATA) {
    try {
      event.target.currentTime = pendingSeekSec;
    } catch {
      // Metadata arrived but the element is not seekable yet.
    }
  }
  isLoading.value = false;
  updatePositionState();
}

function onAudioSeeked(event) {
  if (!isActiveTarget(event.target)) {
    return;
  }
  pendingSeekSec = null;
  if (!isSeeking.value) {
    player.currentTime = event.target.currentTime;
  }
  updatePositionState();
}

function onWaiting(event) {
  if (!isActiveTarget(event.target)) {
    return;
  }
  if (isSeeking.value || pendingSeekSec != null) {
    return;
  }
  isLoading.value = true;
}

function onCanPlay(event) {
  if (!isActiveTarget(event.target)) {
    return;
  }
  isLoading.value = false;
}

function onError(event) {
  if (event.target === standbyEl()) {
    delete event.target.dataset.trackSrc;
    return;
  }
  isLoading.value = false;
}

function onEnded(event) {
  if (!isActiveTarget(event.target)) {
    return;
  }
  player.next();
}

function onPlay(event) {
  if (
    Date.now() < ignoreMediaEventsUntil ||
    !isActiveTarget(event.target) ||
    event.target.muted
  ) {
    return;
  }
  player.isPlaying = true;
  updateMediaSession();
}

function onPause(event) {
  if (
    Date.now() < ignoreMediaEventsUntil ||
    !isActiveTarget(event.target) ||
    event.target.ended ||
    event.target.muted
  ) {
    return;
  }
  player.isPlaying = false;
  updateMediaSession();
}


function updatePositionState() {
  if (!("mediaSession" in navigator)) {
    return;
  }
  const total = Number(duration.value) || 0;
  const position = Number(player.currentTime) || 0;
  if (!total || !Number.isFinite(total) || !Number.isFinite(position)) {
    return;
  }
  try {
    navigator.mediaSession.setPositionState({
      duration: total,
      playbackRate: 1,
      position: Math.min(position, total),
    });
  } catch {
    // Safari throws if duration is 0 or position is out of range.
  }
}

function updateMediaSession() {
  if (!("mediaSession" in navigator)) {
    return;
  }
  const track = player.currentTrack;
  if (!track) {
    navigator.mediaSession.metadata = null;
    navigator.mediaSession.playbackState = "none";
    return;
  }

  const artworkUrl = absoluteUrl(coverUrl.value);
  navigator.mediaSession.metadata = new MediaMetadata({
    title: track.title || "",
    artist: artistName.value,
    album: albumTitle.value,
    artwork: artworkUrl
      ? [{ src: artworkUrl, sizes: "512x512" }]
      : [],
  });
  navigator.mediaSession.playbackState = player.isPlaying ? "playing" : "paused";
  updatePositionState();
}

function bindMediaSessionHandlers() {
  if (!("mediaSession" in navigator)) {
    return;
  }
  const handlers = {
    play: () => {
      player.isPlaying = true;
    },
    pause: () => {
      player.isPlaying = false;
    },
    stop: () => {
      player.stop();
    },
    previoustrack: () => {
      player.prev();
    },
    nexttrack: () => {
      player.next();
    },
    seekto: (details) => {
      if (details?.seekTime == null) {
        return;
      }
      applySeek(details.seekTime);
    },
  };
  for (const [action, handler] of Object.entries(handlers)) {
    try {
      navigator.mediaSession.setActionHandler(action, handler);
    } catch {
      // Unsupported action on this browser.
    }
  }
}

function clearMediaSession() {
  if (!("mediaSession" in navigator)) {
    return;
  }
  navigator.mediaSession.metadata = null;
  navigator.mediaSession.playbackState = "none";
  for (const action of [
    "play",
    "pause",
    "stop",
    "previoustrack",
    "nexttrack",
    "seekto",
  ]) {
    try {
      navigator.mediaSession.setActionHandler(action, null);
    } catch {
      // Unsupported action on this browser.
    }
  }
}

function endSeekFromPointer() {
  if (!isSeeking.value) {
    return;
  }
  applySeek(seekPreview.value);
  isSeeking.value = false;
}

onMounted(() => {
  bindMediaSessionHandlers();
  window.addEventListener("pointerup", endSeekFromPointer);
  window.addEventListener("pointercancel", endSeekFromPointer);
});

onBeforeUnmount(() => {
  clearMediaSession();
  window.removeEventListener("pointerup", endSeekFromPointer);
  window.removeEventListener("pointercancel", endSeekFromPointer);
});

watch(
  () => player.currentTrack,
  () => {
    pendingSeekSec = null;
    isSeeking.value = false;
    seekPreview.value = 0;
  },
);

watch(
  () => [player.currentTrack, player.isPlaying],
  () => {
    syncAudio();
  },
  { flush: "sync" },
);

watch([audioA, audioB], () => {
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
        ref="audioA"
        preload="auto"
        playsinline
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @seeked="onAudioSeeked"
        @waiting="onWaiting"
        @canplay="onCanPlay"
        @error="onError"
        @ended="onEnded"
        @play="onPlay"
        @pause="onPause"
      ></audio>
      <audio
        ref="audioB"
        preload="auto"
        playsinline
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @seeked="onAudioSeeked"
        @waiting="onWaiting"
        @canplay="onCanPlay"
        @error="onError"
        @ended="onEnded"
        @play="onPlay"
        @pause="onPause"
      ></audio>

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
          :value="sliderValue"
          :disabled="duration <= 0"
          class="h-2 min-w-[8rem] flex-1 cursor-pointer accent-white disabled:cursor-not-allowed"
          aria-label="Перемотка"
          @pointerdown="onSeekStart"
          @input="onSeekInput"
          @change="onSeekCommit"
          @pointerup="onSeekCommit"
          @pointercancel="onSeekCommit"
        />

        <span class="shrink-0 text-xs tabular-nums text-gray-400">
          {{ formatTime(sliderValue) }} / {{ formatTime(duration) }}
        </span>

        <button
          v-if="String(player.currentTrack.lyrics || '').trim()"
          type="button"
          class="text-sm text-gray-400 hover:text-white"
          @click="player.openLyrics(player.currentTrack)"
        >
          Текст
        </button>

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
