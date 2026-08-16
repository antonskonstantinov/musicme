<script setup>
import { onBeforeUnmount, ref } from "vue";

import Modal from "../ui/Modal.vue";
import { useCatalogStore } from "../../stores/catalog.js";
import { useFiltersStore } from "../../stores/filters.js";

const catalog = useCatalogStore();
const filters = useFiltersStore();

const searchInput = ref("");
const isSearchLoading = ref(false);
const isOauthModalOpen = ref(false);

let debounceTimer = null;
let searchRequestId = 0;

function openOauthModal() {
  isOauthModalOpen.value = true;
}

function closeOauthModal() {
  isOauthModalOpen.value = false;
}

function onSearchInput(event) {
  searchInput.value = event.target.value;
  isSearchLoading.value = false;
  clearTimeout(debounceTimer);

  debounceTimer = setTimeout(async () => {
    const query = searchInput.value.trim();
    filters.setSearchQuery(query);

    if (query.length === 0) {
      catalog.clearSearch();
      isSearchLoading.value = false;
      return;
    }

    if (query.length < 2) {
      return;
    }

    const requestId = ++searchRequestId;
    isSearchLoading.value = true;
    try {
      await catalog.search(query);
    } finally {
      if (requestId === searchRequestId) {
        isSearchLoading.value = false;
      }
    }
  }, 500);
}

onBeforeUnmount(() => {
  clearTimeout(debounceTimer);
});
</script>

<template>
  <header
    class="flex flex-wrap items-center gap-3 border-b border-gray-800 bg-gray-900 px-4 py-3"
  >
    <div class="shrink-0 text-2xl font-bold tracking-tight text-white">
      Muzzzic
    </div>

    <div class="relative order-3 w-full flex-1 md:order-none md:max-w-xl">
      <input
        type="search"
        :value="searchInput"
        placeholder="Поиск"
        class="w-full rounded-full border border-gray-700 bg-gray-800 py-2 pl-4 pr-10 text-sm text-white placeholder:text-gray-500 focus:border-gray-500 focus:outline-none"
        @input="onSearchInput"
      />
      <span
        v-if="isSearchLoading"
        class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin rounded-full border-2 border-gray-600 border-t-white"
      />
    </div>

    <div class="ml-auto flex shrink-0 items-center gap-2">
      <button
        type="button"
        class="flex items-center gap-2 rounded-md bg-white px-2.5 py-1.5 text-sm font-medium text-gray-800 shadow-sm hover:shadow"
        @click="openOauthModal"
      >
        <svg class="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="#4285F4"
            d="M23.49 12.27c0-.79-.07-1.54-.2-2.27H12v4.51h6.48c-.28 1.5-1.13 2.77-2.4 3.62v3h3.88c2.27-2.09 3.53-5.17 3.53-8.86z"
          />
          <path
            fill="#34A853"
            d="M12 24c3.24 0 5.96-1.07 7.95-2.87l-3.88-3c-1.08.72-2.47 1.15-4.07 1.15-3.13 0-5.78-2.11-6.73-4.96H1.27v3.09C3.25 21.3 7.31 24 12 24z"
          />
          <path
            fill="#FBBC05"
            d="M5.27 14.32A7.21 7.21 0 0 1 4.89 12c0-.81.14-1.59.38-2.32V6.59H1.27A11.99 11.99 0 0 0 0 12c0 1.94.46 3.77 1.27 5.41l4-3.09z"
          />
          <path
            fill="#EA4335"
            d="M12 4.75c1.76 0 3.34.6 4.58 1.79l3.43-3.43C17.95 1.19 15.24 0 12 0 7.31 0 3.25 2.7 1.27 6.59l4 3.09C6.22 6.86 8.87 4.75 12 4.75z"
          />
        </svg>
        <span class="hidden sm:inline">Google</span>
      </button>

      <button
        type="button"
        class="flex items-center gap-2 rounded-md bg-[#FFCC00] px-2.5 py-1.5 text-sm font-medium text-black shadow-sm hover:shadow"
        @click="openOauthModal"
      >
        <svg class="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="#FC3F1D"
            d="M12.6 2h-2.4c-3.5 0-5.7 1.8-5.7 4.7 0 2.4 1.1 3.8 3.3 5.1l.7.4-4.2 6.3h2.8l4.1-6.2h.2V18h2.4V2h-1.2zm-2.3 8.4c-1.7-.9-2.5-1.9-2.5-3.5 0-1.8 1.2-2.8 3.3-2.8h.4v6.6l-1.2-.3z"
          />
        </svg>
        <span class="hidden sm:inline">Яндекс</span>
      </button>

      <button
        type="button"
        class="flex items-center gap-2 rounded-md bg-[#0077FF] px-2.5 py-1.5 text-sm font-medium text-white shadow-sm hover:shadow"
        @click="openOauthModal"
      >
        <svg class="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="#ffffff"
            d="M12.8 17.5c-5.4 0-8.5-3.7-8.6-9.9h2.7c.1 4.6 2.1 6.5 3.7 6.9V7.6h2.5v3.9c1.6-.2 3.2-2 3.8-3.9h2.5c-.4 2.5-2.2 4.3-3.5 5.1 1.3.7 3.3 2.3 4 5.7h-2.8c-.6-2-2.1-3.5-4-3.7v3.7h-.3z"
          />
        </svg>
        <span class="hidden sm:inline">VK</span>
      </button>
    </div>
  </header>

  <Teleport to="body">
    <Transition name="modal-fade">
      <Modal v-if="isOauthModalOpen" @close="closeOauthModal">
        Раздел в разработке
      </Modal>
    </Transition>
  </Teleport>
</template>
