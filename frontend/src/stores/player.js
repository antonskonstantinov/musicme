import { defineStore } from "pinia";
import { ref } from "vue";

function hasMinus(track) {
  return Boolean(track?.minus_url);
}

export const usePlayerStore = defineStore("player", () => {
  const currentTrack = ref(null);
  const isPlaying = ref(false);
  const isMinus = ref(false);
  const currentTime = ref(0);
  const duration = ref(0);
  const queue = ref([]);
  const currentIndex = ref(-1);

  function playTrack(track, nextQueue, options = {}) {
    const playInstrumental = Boolean(options.minus && hasMinus(track));
    currentTrack.value = track;
    if (nextQueue) {
      queue.value = nextQueue;
      const index = nextQueue.findIndex((item) => item.id === track.id);
      currentIndex.value = index >= 0 ? index : 0;
    } else {
      queue.value = [track];
      currentIndex.value = 0;
    }
    isMinus.value = playInstrumental;
    currentTime.value = 0;
    isPlaying.value = true;
  }

  function playMinus(track, nextQueue) {
    if (!hasMinus(track)) {
      return;
    }
    playTrack(track, nextQueue, { minus: true });
  }

  function togglePlay() {
    if (!currentTrack.value) {
      return;
    }
    isPlaying.value = !isPlaying.value;
  }

  function stop() {
    isPlaying.value = false;
    isMinus.value = false;
    currentTrack.value = null;
    currentTime.value = 0;
    duration.value = 0;
    queue.value = [];
    currentIndex.value = -1;
  }

  function seekTo(seconds) {
    const value = Number(seconds);
    if (!Number.isFinite(value)) {
      return;
    }
    const max = Number(duration.value);
    if (Number.isFinite(max) && max > 0) {
      currentTime.value = Math.min(Math.max(0, value), max);
      return;
    }
    currentTime.value = Math.max(0, value);
  }

  function peekNextTrack() {
    if (!queue.value.length || currentIndex.value < 0) {
      return null;
    }
    return queue.value[(currentIndex.value + 1) % queue.value.length];
  }

  function next() {
    if (!queue.value.length || currentIndex.value < 0) {
      isPlaying.value = false;
      return;
    }
    currentIndex.value = (currentIndex.value + 1) % queue.value.length;
    currentTrack.value = queue.value[currentIndex.value];
    isMinus.value = false;
    currentTime.value = 0;
    isPlaying.value = true;
  }

  function prev() {
    if (!queue.value.length || currentIndex.value < 0) {
      return;
    }
    currentIndex.value =
      (currentIndex.value - 1 + queue.value.length) % queue.value.length;
    currentTrack.value = queue.value[currentIndex.value];
    isMinus.value = false;
    currentTime.value = 0;
    isPlaying.value = true;
  }

  const lyricsTrack = ref(null);

  function openLyrics(track) {
    if (!String(track?.lyrics || "").trim()) {
      return;
    }
    lyricsTrack.value = track;
  }

  function closeLyrics() {
    lyricsTrack.value = null;
  }

  return {
    currentTrack,
    isPlaying,
    isMinus,
    currentTime,
    duration,
    queue,
    currentIndex,
    lyricsTrack,
    playTrack,
    playMinus,
    togglePlay,
    stop,
    seekTo,
    peekNextTrack,
    next,
    prev,
    openLyrics,
    closeLyrics,
  };
});
