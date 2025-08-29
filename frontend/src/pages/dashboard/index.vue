<script setup lang="ts">
import { computed, watch } from 'vue';
definePageMeta({ layout: "full-width" });

// Get runtime configuration (may be used for API endpoints)
const config = useRuntimeConfig();

/*******************************
 * 
 * Site List
 * 
********************************/
const sitesList = useAllSites();
sitesList.fetchAllSites();

/**
 * Computed property to transform site data for v-select component
 * Converts raw site objects into the format expected by Vuetify's v-select
 * 
 * Format: {title: "display text", value: "option value"}
 * Display shows: "site_prefix, site_name" (e.g., "ABC, Test Site")
 */
const sites = computed(() => {
  // Return empty array if no data available
  if (!sitesList.data.value) return [];
  
  // Transform each site into dropdown option format
  return sitesList.data.value.map(site => ({
    title: `${site.prefix}, ${site.name}`,  // Display format: "PREFIX, Name"
    value: site.id                          // Value used for filtering
  }));
});

// Wait until the site list is fetched, then print the list to the console
watch(
  () => sitesList.pending.value,
  (loading) => {
    if (!loading && sites.value.length > 0) {
      console.log("Fetched sites:", sites.value);
    }
  }
);


/*******************************
 * 
 * Models List
 * 
********************************/

const modelList = useAllModels();
modelList.fetchAllModels();

// Wait until the model list is fetched, then print the list to the console
watch(
  () => modelList.pending?.value,
  (loading) => {
    if (!loading && modelList.data?.value && modelList.data.value.length > 0) {
      console.log("Fetched models:", modelList.data.value);
    }
  }
);

/*******************************
 * 
 * Years List
 * 
********************************/
const yearsList = useRecordYears();
yearsList.fetchYears();

watch(
  () => yearsList.pending.value,
  (loading) => {
    if (!loading && yearsList.data.value.length > 0) {
      console.log("Fetched years:", yearsList.data.value);
    }
  }
);

/*******************************
 * 
 * Set default threshold
 * 
********************************/
const threshold = 0.5;


/*******************************
 * 
 * Species list
 * 
********************************/
const speciesLabelsSearch = useLabelsSearch();
speciesLabelsSearch.searchLabels("%%%");  // will get the fits 50 labels (for testing)

watch(
  () => speciesLabelsSearch.data.value,
  (labels) => {
    if (labels && labels.length > 0) {
      console.log("Fetched all species labels:", labels);
    }
  },
  { immediate: true }
);

</script>

<template>
  <v-container>
  </v-container>
</template>
