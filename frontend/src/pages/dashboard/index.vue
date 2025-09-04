<script setup lang="ts">
import { computed, watch, ref } from 'vue';
import PageControls from '@/components/dashboard/PageControls.vue'

definePageMeta({ layout: "full-width" });

console.log("Component setup starting");

// Get runtime configuration (may be used for API endpoints)
const config = useRuntimeConfig();

// call this first!
// selected parameters to pass to Dashboard
const selectedParams = ref({
  model: null,
  sites: [],
  year: null,
  species: null,
  threshold: 0.5
});

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
 * Species list
 * 
********************************/
const speciesLabelsSearch = useLabelsSearch();

// Watch for changes in selections to trigger species search
watch(
  () => [
    selectedParams.value.model, 
    selectedParams.value.sites, 
    selectedParams.value.year,
    selectedParams.value.threshold
  ],
  ([model, sites, year, threshold]) => {
    // Safety check
    if (!selectedParams || !selectedParams.value) {
      console.error("selectedParams is undefined");
      return;
    }
    // Clear any pending search operations
    if (speciesLabelsSearch.pendingSearch) {
      speciesLabelsSearch.pendingSearch.cancel();
    }

    // Only search for species when all required parameters are available
    if (model && sites && Array.isArray(sites) && sites.length > 0 && year) {
      console.log("Searching for species with:", 
        "Model:", model.value, 
        "Site:", sites[0].value, 
        "Year:", year,
        "Threshold:", threshold);
      
      // Add a small delay to ensure all reactive updates have completed
      setTimeout(() => {
        // Use the first selected site for now (could be enhanced to handle multiple sites)
        speciesLabelsSearch.searchLabels(model.value, sites[0].value, threshold, year);
      }, 0);
    } else {
      // Reset species data when parameters are missing
      if (speciesLabelsSearch.data.value) {
        // Use a non-reactive way to clear the data
        speciesLabelsSearch.data.value = null;
      }
      console.log("Not all parameters available for species search");
    }
  },
  { immediate: true, deep: true } // Add deep: true to detect nested changes in arrays
);

const formattedSpecies = computed(() => {
  // Check if we're currently loading species data
  if (speciesLabelsSearch.pending.value) {
    return [{
      title: "Loading species...",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }

  // Extract the raw species data
  const speciesData = speciesLabelsSearch.data?.value?.labels;

  if (!speciesData) {
    // Create a placeholder message
    let message = "Please choose a classifier, a site and a year to display species";
    return [{
      title: message,
      value: null,
      disabled: true,
      isPlaceholder: true 
    }];
  }
  // For empty arrays, show a different message
  if (Array.isArray(speciesData) && speciesData.length === 0) {
    return [{
      title: "No species found with current selections",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }

  // Process the data - use a try/catch to prevent errors
  try {
    // Convert to array if necessary
    const processedSpecies = Array.isArray(speciesData) ? 
      speciesData : Array.from(speciesData);
    
    return processedSpecies.map(species => ({
      title: species.name,
      value: species.id,
      isPlaceholder: false
    }));

  } catch (e) {
    console.error("Error processing species data:", e);
    return [{
      title: "Error processing species data",
      value: null,
      disabled: true,
      isPlaceholder: true
    }];
  }
});

/***********************************************
 * 
 * Handle selection updates from PageControls
 * 
 ***********************************************/
const handleSelectionUpdate = (selection) => {
  //  console.log('Selected model:', selection.model);
  //  console.log('Selected sites:', selection.sites);
  //  console.log('Selected year:', selection.year);
  //  console.log('Selected species:', selection.species);
  //  console.log('Selected threshold:', selection.threshold);

  // Safely update each property individually
  if ('model' in selection) selectedParams.value.model = selection.model;
  if ('sites' in selection) selectedParams.value.sites = selection.sites;
  if ('year' in selection) selectedParams.value.year = selection.year;
  if ('species' in selection) selectedParams.value.species = selection.species;
  if ('threshold' in selection) selectedParams.value.threshold = selection.threshold;
};

// Create a computed property for the iframe URL with query parameters
const dashboardAppUrl = computed(() => {
  // Make sure selectedParams exists before accessing its properties
  if (!selectedParams || !selectedParams.value) {
    console.error("selectedParams is undefined");
    return "http://localhost:9090/"; // Return base URL without parameters
  }

  const params = new URLSearchParams();
  
  try {
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
      const speciesId = selectedParams.value.species;
      params.append('species', selectedParams.value.species);

      // Find the species name from formattedSpecies
      const speciesItems = formattedSpecies.value;
      const selectedSpecies = speciesItems.find(item => 
        item.value === speciesId && !item.isPlaceholder
      );
      
      // Add the species name if found
      if (selectedSpecies && selectedSpecies.title) {
        params.append('speciesName', encodeURIComponent(selectedSpecies.title));
        console.log(`Added species name: ${selectedSpecies.title} for ID: ${speciesId}`);
      } else {
        // Try to find the species directly from the raw data
        const rawSpecies = speciesLabelsSearch.data?.value?.labels?.find(s => s.id === speciesId);
        if (rawSpecies && rawSpecies.name) {
          params.append('speciesName', encodeURIComponent(rawSpecies.name));
          console.log(`Added species name from raw data: ${rawSpecies.name}`);
        }
      }
    }
    
    // Add threshold parameter with default
    if (selectedParams.value.threshold !== undefined) {
      params.append('threshold', selectedParams.value.threshold.toString());
    } else {
      params.append('threshold', "0.5");  // Fallback default
    }
  } catch (e) {
    console.error("Error generating dashboard URL:", e);
    return "http://localhost:9090/"; // Return base URL in case of errors
  }

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

console.log("Component setup completed");
console.log("Initial selectedParams:", selectedParams.value);
</script>

<template>
  <v-container style="max-width: 100%;">
    <v-row>
      <!-- Left column -->
      <v-col cols="4">
        <PageControls
          :available-models="modelList.data?.value || []"
          :available-sites="sites"
          :available-years="yearsList.data?.value || []"
          :available-species="formattedSpecies"
          :default-threshold="0.5"
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