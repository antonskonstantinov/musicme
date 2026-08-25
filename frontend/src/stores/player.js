import { defineStore } from "pinia";
import { ref } from "vue";

export const usePlayerStore = defineStore("player", () => {
  const currentTrack = ref(null);
  const isPlaying = ref(false);
  const currentTime = ref(0);
  const duration = ref(0);
  const queue = ref([]);
  const currentIndex = ref(-1);

  function playTrack(track, nextQueue) {
    currentTrack.value = track;
    if (nextQueue) {
      queue.value = nextQueue;
      const index = nextQueue.findIndex((item) => item.id === track.id);
      currentIndex.value = index >= 0 ? index : 0;
    } else {
      queue.value = [track];
      currentIndex.value = 0;
    }
    currentTime.value = 0;
    isPlaying.value = true;
  }

  function togglePlay() {
    if (!currentTrack.value) {
      return;
    }
    isPlaying.value = !isPlaying.value;
  }

  function stop() {
    isPlaying.value = false;
    currentTrack.value = null;
    currentTime.value = 0;
    duration.value = 0;
    queue.value = [];
    currentIndex.value = -1;
  }

  function seekTo(seconds) {
    currentTime.value = seconds;
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
    currentTime,
    duration,
    queue,
    currentIndex,
    lyricsTrack,
    playTrack,
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
