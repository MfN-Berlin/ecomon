<template>
  <v-switch
    v-model="isDarkMode"
    color="primary"
    :prepend-icon="isDarkMode ? 'mdi-weather-night' : 'mdi-weather-sunny'"
    @change="toggleTheme"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";

import { useUiStore } from "@/stores/ui";

// Adjust the import path as needed

const uiStore = useUiStore();

const isDarkMode = computed(() => uiStore.darkMode);

function toggleTheme() {
  uiStore.toggleDarkMode();
}
</script>
