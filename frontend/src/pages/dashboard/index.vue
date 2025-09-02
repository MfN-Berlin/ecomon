<script setup lang="ts">
import { computed, watch, ref } from 'vue';
import PageControls from '@/components/dashboard/PageControls.vue'

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

/*******************************
 * 
 * Models List
 * 
********************************/

const modelList = useAllModels();
modelList.fetchAllModels();

/*******************************
 * 
 * Years List
 * 
********************************/
const yearsList = useRecordYears();
yearsList.fetchYears();

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
speciesLabelsSearch.searchLabels(3, 2, 0.5);

watch(
  () => speciesLabelsSearch.data.value,
  (labels) => {
    if (labels && labels.length > 0) {
      console.log("Fetched all species labels:", labels);
    }
  },
  { immediate: true }
);

const formattedSpecies = computed(() => {
  const speciesData = speciesLabelsSearch.data?.value?.labels || [];
  
  // Return the labels array formatted for v-select
  return speciesData.map(species => ({
    title: species.name,  // Display name
    value: species.id     // Actual value
  }));
});

/***********************************************
 * 
 * Handle selection updates from PageControls
 * 
 ***********************************************/
// selected parameters to pass to Dashboard
const selectedParams = ref({
  model: null,
  sites: [],
  year: null,
  species: null
});

const handleSelectionUpdate = (selection) => {
  //  console.log('Selected model:', selection.model);
  //  console.log('Selected sites:', selection.sites);
  //  console.log('Selected year:', selection.year);
  //  console.log('Selected species:', selection.species);

  // Update the selectedParams ref with the new values
  selectedParams.value = selection;
};

// Create a computed property for the iframe URL with query parameters
const dashboardAppUrl = computed(() => {
  const params = new URLSearchParams();
  
  // Add model parameter if available
  if (selectedParams.value.model) {
    params.append('model', selectedParams.value.model.value);
    params.append('modelName', selectedParams.value.model.title);
  }
  
  // Add sites parameter if available
  if (selectedParams.value.sites && selectedParams.value.sites.length > 0) {
    const siteIds = selectedParams.value.sites.map(site => site.value).join(',');
    params.append('sites', siteIds);
    
    // Also add site titles for display in the dashboard
    const siteTitles = selectedParams.value.sites.map(site => site.title).join('|');
    params.append('siteTitles', encodeURIComponent(siteTitles));
    // console.log("Site titles added:", siteTitles);
  }
  
  // Add year parameter if available
  if (selectedParams.value.year) {
    params.append('year', selectedParams.value.year);
  }
  
  // Add species parameter if available
  if (selectedParams.value.species) {
    params.append('species', selectedParams.value.species);
  }
  
  // Add threshold parameter
  params.append('threshold', threshold.toString());
  
  // Return the base URL with query parameters
  return `http://localhost:9090/?${params.toString()}`;
});

watch(
  () => speciesLabelsSearch.data.value,
  (labels) => {
    console.log("Species labels type:", typeof labels);
    console.log("Is array?", Array.isArray(labels));
    console.log("Structure:", JSON.stringify(labels).slice(0, 100));
    if (labels && labels.length > 0) {
      console.log("Fetched all species labels:", labels);
    }
  },
  { immediate: true }
);
</script>

<template>
  <v-container style="max-width: 100%;">
    <v-row>
      <!-- Left column -->
      <v-col cols="4">
        <PageControls
          v-if="sites.length > 0"
          :available-models="modelList.data?.value || []"
          :available-sites="sites"
          :available-years="yearsList.data?.value || []"
          :available-species="formattedSpecies"
          @update:selection="handleSelectionUpdate"
        />
      </v-col>
      <!-- Main content column -->
      <v-col cols="8">
        <div style="height: 800px;">
          <iframe
            :src="dashboardAppUrl"
            style="width: 100%; height: 100%; border: none;"
            title="Dashboard App"
            ref="dashboardFrame"
          ></iframe>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>
