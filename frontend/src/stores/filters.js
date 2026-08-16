import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useFiltersStore = defineStore("filters", () => {
  const selectedGenre = ref(null);
  const selectedMood = ref(null);
  const selectedArtist = ref(null);
  const selectedAlbum = ref(null);
  const searchQuery = ref("");

  const activeFilters = computed(() => {
    const filters = [];

    if (selectedGenre.value) {
      filters.push({
        type: "genre",
        label: `Жанр: ${selectedGenre.value.name}`,
      });
    }
    if (selectedMood.value) {
      filters.push({
        type: "mood",
        label: `Настроение: ${selectedMood.value.name}`,
      });
    }
    if (selectedArtist.value) {
      filters.push({
        type: "artist",
        label: `Артист: ${selectedArtist.value.name}`,
      });
    }
    if (selectedAlbum.value) {
      filters.push({
        type: "album",
        label: `Альбом: ${selectedAlbum.value.title}`,
      });
    }

    return filters;
  });

  const activeFiltersCount = computed(() => activeFilters.value.length);
  const hasActiveFilters = computed(() => activeFiltersCount.value > 0);
  const isDefaultState = computed(
    () => !hasActiveFilters.value && searchQuery.value === "",
  );

  function setGenre(genre) {
    selectedGenre.value = genre;
  }

  function setMood(mood) {
    selectedMood.value = mood;
  }

  function setArtist(artist) {
    selectedArtist.value = artist;
  }

  function setAlbum(album) {
    selectedAlbum.value = album;
  }

  function clearGenre() {
    selectedGenre.value = null;
  }

  function clearMood() {
    selectedMood.value = null;
  }

  function clearArtist() {
    selectedArtist.value = null;
  }

  function clearAlbum() {
    selectedAlbum.value = null;
  }

  function resetAll() {
    selectedGenre.value = null;
    selectedMood.value = null;
    selectedArtist.value = null;
    selectedAlbum.value = null;
  }

  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  return {
    selectedGenre,
    selectedMood,
    selectedArtist,
    selectedAlbum,
    searchQuery,
    activeFilters,
    activeFiltersCount,
    hasActiveFilters,
    isDefaultState,
    setGenre,
    setMood,
    setArtist,
    setAlbum,
    clearGenre,
    clearMood,
    clearArtist,
    clearAlbum,
    resetAll,
    setSearchQuery,
  };
});
