<script setup lang="ts">
import PageControls from '~/components/dashboard/PageControls.vue';

definePageMeta({ layout: "full-width" });

// Initialize data fetching composables
const sitesList = useAllSites();
const modelList = useAllModels();
const yearsList = useRecordYears();

// Fetch data
sitesList.fetchAllSites();
modelList.fetchAllModels();
yearsList.fetchYears();

// Species handling
const speciesLabelsSearch = useLabelsSearch();
const preservedSpeciesSelection = ref(null);

// Transform site data for v-select component
const sites = computed(() => {
  if (!sitesList.data.value) return [];

  return sitesList.data.value.map(site => ({
    title: `${site.prefix}, ${site.name}`,
    value: site.id
  }));
});

// Handle selection updates from PageControls
const selectedParams = ref({
  model: null,
  sites: [],
  year: null,
  species: null,
  threshold: 0.5 // Add threshold to selectedParams
});

// MaxValue selection
const maxValueOption = ref('per_recording');
const sampleNumber = ref(100); // Default sample number

// Watch for changes in selections to trigger species search
watch(
  () => [
    selectedParams.value.model,
    selectedParams.value.sites,
    selectedParams.value.year
  ],
  ([model, sites, year]) => {
    // Store the current species selection before search
    if (selectedParams.value.species) {
      preservedSpeciesSelection.value = selectedParams.value.species;
    }

    // Clear any pending search operations
    if (speciesLabelsSearch.pendingSearch) {
      speciesLabelsSearch.pendingSearch.cancel();
    }

    // Only search for species when all required parameters are available
    if (model && sites && Array.isArray(sites) && sites.length > 0 && year) {
      console.log("Searching for species with:",
        "Model:", model.value,
        "Sites:", sites.map(site => site.value),
        "Year:", year);

      speciesLabelsSearch.searchLabels(model.value, sites.map(site => site.value), year);
    } else {
      // Only clear species data if required parameters are missing
      if (speciesLabelsSearch.data.value) {
        speciesLabelsSearch.data.value = null;
      }
      console.log("Not all parameters available for species search");
    }
  },
  { immediate: true, deep: true }
);

// Watch for when species search completes and restore the selection
watch(
  () => speciesLabelsSearch.data.value,
  (labels) => {
    if (labels && labels.labels && labels.labels.length > 0) {
      console.log("Fetched species labels:", labels);

      // Restore the preserved species selection if it exists in the new data
      if (preservedSpeciesSelection.value) {
        const speciesExists = labels.labels.some(
          species => species.id === preservedSpeciesSelection.value
        );

        if (speciesExists) {
          console.log("Restoring species selection:", preservedSpeciesSelection.value);
          selectedParams.value.species = preservedSpeciesSelection.value;
        } else {
          console.log("Previously selected species not available in new site");
          preservedSpeciesSelection.value = null;
        }
      }
    }
  },
  { immediate: true }
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
    return [{
      title: "Please choose a classifier, a site and a year to display species",
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

  // Process the data
  try {
    return speciesData.map(species => ({
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

const handleSelectionUpdate = (selection) => {
  // Safely update each property individually
  if ('model' in selection) selectedParams.value.model = selection.model;
  if ('sites' in selection) selectedParams.value.sites = selection.sites;
  if ('year' in selection) selectedParams.value.year = selection.year;
  if ('species' in selection && selection.species !== undefined) {
    selectedParams.value.species = selection.species;
  }
  if ('threshold' in selection) selectedParams.value.threshold = selection.threshold;
};

// Create params for minutes query
const minutesParams = computed(() => {
  const { model, sites, year, species, threshold } = selectedParams.value;

  if (!model || !sites || sites.length === 0 || !year || !species) {
    return null;
  }

  return {
    speciesId: species,
    modelId: model.value,
    siteId: sites[0].value,
    year: year,
    threshold: threshold
  };
});

// Use the composable
const {
  data: minutesWithActivity,
  isFetching: isLoadingMinutes,
  isError: isMinutesError
} = useMinutesWithActivity(minutesParams);

// Tooltip texts in English
const tooltipTexts = {
  per_recording: 'Default method: Simple and reliable for any recording length',
  per_minute: 'Ideal method but complex: Handles recordings by minute segments',
  per_signal: 'Advanced method: Ensures non-overlapping signals',
  all: 'For statistical sampling: Includes all values, not just the maximum',
  sample_number: 'Number of samples to draw from the selected recordings'
};

</script>

<template>
  <v-container style="max-width: 100%;">
    <v-row>
      <!-- Left column with controls -->
      <v-col cols="4">
        <PageControls
          :available-models="modelList.data?.value || []"
          :available-sites="sites"
          :available-years="yearsList.data?.value || []"
          :available-species="formattedSpecies"
          :default-threshold="selectedParams.threshold"
          @update:selection="handleSelectionUpdate"
        />
      </v-col>

      <!-- Right column for voucher content -->
      <v-col cols="8">
        <!-- Threshold control at the top -->
        <v-card class="page-controls v-theme--mfnLight mb-4" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
          <v-card-text>
            <div class="control-row horizontal align-inputs">
              <label for="threshold-input" class="label-inline text-right">Threshold</label>
              <div class="input-with-hint">
                <v-text-field
                  id="threshold-input"
                  v-model.number="selectedParams.threshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  density="compact"
                  class="threshold-input"
                  @update:model-value="handleSelectionUpdate({ threshold: selectedParams.threshold })"
                ></v-text-field>
                <span class="hint-text">Range: 0.01 to 1.00</span>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <!-- Sampling Method control -->
        <v-card class="page-controls v-theme--mfnLight mb-4" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
          <v-card-text>
            <div class="control-row">
              <label class="label-inline">Sampling Method</label>
              <v-radio-group v-model="maxValueOption" inline class="radio-group-spacing">
                <div class="radio-option-container">
                  <div class="radio-with-tooltip">
                    <v-radio label="Per recording" value="per_recording"></v-radio>
                    <v-tooltip
                      :text="tooltipTexts.per_recording"
                      location="top"
                      open-delay="200"
                      content-class="tooltip-content"
                    >
                      <template v-slot:activator="{ props }">
                        <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                      </template>
                    </v-tooltip>
                  </div>
                </div>

                <div class="radio-option-container">
                  <div class="radio-with-tooltip">
                    <v-radio label="Per minute" value="per_minute" disabled></v-radio>
                    <v-tooltip
                      :text="tooltipTexts.per_minute"
                      location="top"
                      open-delay="200"
                      content-class="tooltip-content"
                    >
                      <template v-slot:activator="{ props }">
                        <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                      </template>
                    </v-tooltip>
                  </div>
                </div>

                <div class="radio-option-container">
                  <div class="radio-with-tooltip">
                    <v-radio label="Per signal" value="per_signal" disabled></v-radio>
                    <v-tooltip
                      :text="tooltipTexts.per_signal"
                      location="top"
                      open-delay="200"
                      content-class="tooltip-content"
                    >
                      <template v-slot:activator="{ props }">
                        <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                      </template>
                    </v-tooltip>
                  </div>
                </div>

                <div class="radio-option-container">
                  <div class="radio-with-tooltip">
                    <v-radio label="All values" value="all" disabled></v-radio>
                    <v-tooltip
                      :text="tooltipTexts.all"
                      location="top"
                      open-delay="200"
                      content-class="tooltip-content"
                    >
                      <template v-slot:activator="{ props }">
                        <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                      </template>
                    </v-tooltip>
                  </div>
                </div>
              </v-radio-group>
            </div>

            <!-- Sample Number Input -->
            <div class="control-row horizontal mt-4">
              <label class="label-inline text-right">Sample Number</label>
              <div class="input-with-tooltip">
                <v-text-field
                  v-model.number="sampleNumber"
                  type="number"
                  min="1"
                  :max="minutesWithActivity || 1000"
                  density="compact"
                  class="sample-number-input"
                  hide-details
                ></v-text-field>
                <v-tooltip
                  :text="tooltipTexts.sample_number"
                  location="top"
                  open-delay="300"
                  content-class="tooltip-content"
                >
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="x-small" class="info-icon">mdi-information</v-icon>
                  </template>
                </v-tooltip>
                <span v-if="selectedParams.species" class="hint-text activity-hint">
                  Available minutes with activity:
                  <template v-if="isLoadingMinutes">
                    Loading...
                  </template>
                  <template v-else-if="isMinutesError">
                    Error
                  </template>
                  <template v-else>
                    {{ minutesWithActivity || 0 }}
                  </template>
                </span>
              </div>
            </div>

          </v-card-text>
        </v-card>

        <!-- Voucher content card -->
        <div style="height: 80%;">
          <v-card
            class="d-flex align-center justify-center"
            style="width: 100%; height: 100%;"
            color="grey-lighten-4"
          >
            <div class="text-center pa-5">
              <v-icon icon="mdi-tag-outline" size="large" color="grey" class="mb-3"></v-icon>
              <p class="text-body-1 text-grey-darken-1">
                Select parameters to view and download voucher
              </p>
            </div>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
/* Threshold input styling */
.threshold-input {
  width: 7em;
  max-width: 7em;
  flex-shrink: 0;
}

.threshold-input :deep(input) {
  text-align: center;
}

/* For horizontal layout controls (label + input + hint on same line) */
.control-row.horizontal {
  flex-direction: row;
  align-items: center;
}

.align-inputs {
  display: grid;
  grid-template-columns: 7em 1fr;
  align-items: center;
  gap: 0.75rem;
}

/* Right-align labels */
.text-right {
  text-align: right;
  margin-right: 0;
}

/* Input with hint on same line */
.input-with-hint {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 1rem;
}

.hint-text {
  color: rgba(0, 0, 0, 0.6);
  font-size: 0.75rem;
  white-space: nowrap;
}

.label-inline {
  margin-right: 1rem;
  margin-bottom: 0;
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}

/* radio buttons */
.control-row {
  display: flex;
  flex-direction: column;
}

.radio-group-spacing {
  margin-top: 0.25rem;
  position: relative;
}

.radio-group-spacing :deep(.v-selection-control-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.radio-option-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin-right: 1em;
}

.radio-with-tooltip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-icon {
  color: rgba(0, 0, 0, 0.4);
  cursor: help;
  opacity: 0.8;
  transition: opacity 0.2s ease;
  margin-bottom: 1px;
}

.info-icon:hover {
  opacity: 1;
  color: rgba(0, 0, 0, 0.6);
}

.tooltip-content {
  max-width: 300px;
  font-size: 0.8125rem;
  line-height: 1.4;
  background-color: rgba(70, 70, 70, 0.95);
  color: white;
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.v-radio :deep(.v-label) {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.87);
  margin-right: 0;
}

.v-radio:disabled :deep(.v-label) {
  color: rgba(0, 0, 0, 0.38);
  opacity: 1;
}

/* Sample Number Input Styles */
.control-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.control-row.horizontal {
  display: grid;
  grid-template-columns: 7em 1fr;
  align-items: center;
  gap: 0.75rem;
}

.sample-number-input {
  width: 100px;
  max-width: 100px;
}

.sample-number-input :deep(input) {
  text-align: center;
}

.input-with-tooltip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: fit-content;
}

.activity-hint {
  margin-left: 0.5rem;
}

.label-inline {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}
</style>