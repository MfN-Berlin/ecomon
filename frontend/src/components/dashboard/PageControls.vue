<script setup>
import { ref, computed, watch } from 'vue';
import { debounce } from 'lodash-es';

const props = defineProps({
  availableModels: {
    type: Array,
    default: () => []
  },
  availableSites: {
    type: Array,
    default: () => []
  },
  availableYears: {
    type: Array,
    default: () => ['2023', '2024', '2025']  // get this from the db
  },
  availableSpecies: {
    type: Array,
    default: () => ['']
  },
  defaultThreshold: {
    type: Number,
    default: 0.5
  }
});

const emit = defineEmits(['update:selection']);

// Initialize all reactive variables at the top
const selectedModel = ref(null);
const selectedSites = ref([]);
const selectedYear = ref(null);
const selectedSpecies = ref(null);
const selectedSpeciesName = ref(null);
const threshold = ref(props.defaultThreshold);
const isUpdatingThreshold = ref(false);
let thresholdTimeoutId = null;

// Check if the species list contains only a placeholder
const hasOnlyPlaceholder = computed(() => {
  return props.availableSpecies.length === 1 &&
         props.availableSpecies[0]?.isPlaceholder === true;
});

// Helper function to get species name
function getSpeciesName(speciesValue) {
  return selectedSpeciesName.value || null;
}

// Get placeholder message for hint/help text
const placeholderMessage = computed(() => {
  if (hasOnlyPlaceholder.value) {
    return props.availableSpecies[0]?.title || '';
  }
  return '';
});
const speciesCountMessage = computed(() => {
  if (!hasOnlyPlaceholder.value && props.availableSpecies.length > 0) {
    return `${props.availableSpecies.length} species found`;
  }
  return null; // No message if no species are found or placeholder applies
});

/***************
 *
 * Selection update
 *
****************/

// Function called when non-threshold values change
function updateSelection() {
  console.log("Updating selection:", {
    model: selectedModel.value,
    sites: selectedSites.value,
    year: selectedYear.value,
    species: selectedSpecies.value,
    threshold: threshold.value
  });
  emit('update:selection', {
    model: selectedModel.value,
    sites: selectedSites.value,
    year: selectedYear.value,
    species: selectedSpecies.value || null, // Preserve species selection
    threshold: threshold.value
  });
}

// Function to update species with debounce
const debouncedUpdateSpecies = debounce(() => {
  updateSelection();
}, 1000);

// Function to update threshold with debounce
const debouncedUpdateSelection = debounce(() => {
  updateSelection();
}, 300);

// Function to update threshold with debounce - without triggering species update
const debouncedUpdateThreshold = debounce(() => {
  emit('update:selection', {
    model: selectedModel.value,
    sites: selectedSites.value,
    year: selectedYear.value,
    species: selectedSpecies.value, // Keep the current species selection unchanged
    threshold: threshold.value
  });
}, 300);

function updateThreshold() {
  isUpdatingThreshold.value = true;

  // Clear any existing timeout
  if (thresholdTimeoutId) {
    clearTimeout(thresholdTimeoutId);
  }

  debouncedUpdateThreshold();

  // Reset the flag after the debounce delay + a small buffer
  thresholdTimeoutId = setTimeout(() => {
    isUpdatingThreshold.value = false;
    thresholdTimeoutId = null;
  }, 1000);
}
/***************
 *
 * Models logic
 *
****************/

// Models
// Transform models for v-select if needed (depends on your v-select component requirements)
const models = computed(() => {
  return props.availableModels.map(model => ({
    title: model.name,
    value: model.id
  }));
});

// Watch for available models changes - DON'T auto-select
watch(
  () => props.availableModels,
  (newModels) => {
    // No auto-selection
    updateSelection();
  },
  { immediate: true }
);

/***************
 *
 * Sites logic
 *
****************/

// Available sites (those not yet selected)
const availableSitesList = computed(() => {
  if (!props.availableSites || !Array.isArray(props.availableSites)) {
    console.log("No available sites or not an array");
    return [];
  }

  // Filter out sites that are already selected
  const filtered = props.availableSites.filter(site =>
    !selectedSites.value.some(s => s.value === site.value)
  );

  return filtered;
});

// Watch for available sites changes to update available list
watch(
  () => props.availableSites,
  () => {
    // When sites list changes, we don't auto-select any
    // but we ensure the availableSitesList is updated
    updateSelection();
  },
  { immediate: true }
);

// Function to select a site
function selectSite(site) {
  // for now, allow only one site to be selected at a time
  // To allow multiple selections, uncomment the line below and comment the next one
  // selectedSites.value.push(site);
  selectedSites.value = [site]; // Set to array with only the new site
  updateSelection();
}

// Function to deselect a site
function deselectSite(site) {
  selectedSites.value = selectedSites.value.filter(s => s.value !== site.value);
  updateSelection();
}

/*******************************
 *
 * Years logic
 *
********************************/
const years = computed(() => props.availableYears);

// Watch for available years changes - DON'T auto-select
watch(
  () => props.availableYears,
  (newYears) => {
    // No auto-selection
    updateSelection();
  },
  { immediate: true }
);

/***************
 *
 * Species logic
 *
****************/

// Get the filtered species list for the dropdown - FIXED THE DUPLICATE COMPUTED PROPERTY
const species = computed(() => {
  console.log("Computing species list:");
  console.log("- hasOnlyPlaceholder:", hasOnlyPlaceholder.value);
  console.log("- selectedSpecies:", selectedSpecies.value);
  console.log("- selectedSpeciesName:", selectedSpeciesName.value);
  console.log("- availableSpecies length:", props.availableSpecies.length);

  // Start with an empty array
  let filteredSpecies = [];

  // If there are non-placeholder species, add them
  if (!hasOnlyPlaceholder.value) {
    filteredSpecies = props.availableSpecies.filter(item => !item.isPlaceholder);
  }

  // Always ensure the currently selected species is included in the dropdown
  if (
    selectedSpecies.value &&
    !filteredSpecies.some(s => s.value === selectedSpecies.value)
  ) {
    const selectedSpeciesItem = props.availableSpecies.find(
      s => s.value === selectedSpecies.value
    );

    if (selectedSpeciesItem) {
      filteredSpecies.push(selectedSpeciesItem);
    } else {
      // If the selected species is not in availableSpecies, create a fallback entry
      // Use the stored species name if available, otherwise fallback to ID
      const speciesName = getSpeciesName(selectedSpecies.value);
      console.log("Creating fallback with speciesName:", speciesName);
      filteredSpecies.push({
        value: selectedSpecies.value,
        title: speciesName ? `${speciesName} (not in list)` : `Species ${selectedSpecies.value} (not in list)`
      });
    }
  }

  return filteredSpecies;
});

watch(
  () => props.availableSpecies,
  (newSpecies) => {
    console.log("availableSpecies changed:");
    console.log("- isUpdatingThreshold:", isUpdatingThreshold.value);
    console.log("- newSpecies length:", newSpecies.length);
    console.log("- selectedSpecies:", selectedSpecies.value);
    console.log("- selectedSpeciesName:", selectedSpeciesName.value);

    // Don't update species selection during threshold updates
    if (isUpdatingThreshold.value) {
      console.log("Skipping species update - threshold is updating");
      return;
    }

    if (hasOnlyPlaceholder.value) {
      console.log("Only placeholder available - clearing selection");
      selectedSpecies.value = null;
      selectedSpeciesName.value = null; // Clear stored name
    } else if (
      selectedSpecies.value &&
      newSpecies.some(s => s.value === selectedSpecies.value)
    ) {
      // If the current selection is valid, update the stored name
      const currentSpecies = newSpecies.find(s => s.value === selectedSpecies.value);
      if (currentSpecies) {
        selectedSpeciesName.value = currentSpecies.title;
        console.log("Updated stored name:", selectedSpeciesName.value);
      }
      return;
    } else if (selectedSpecies.value) {
      // Species is selected but not in new list - keep it selected and preserve the name
      console.log("Species not in new list - preserving selection and name");
      // Don't clear selectedSpecies.value or selectedSpeciesName.value
      return;
    }

    // Only call updateSelection when we actually change selectedSpecies
    debouncedUpdateSpecies();
  },
  { immediate: true }
);

// Watch for species selection changes to store the name
// Watch for species selection changes to store the name
watch(
  () => selectedSpecies.value,
  (newSpeciesValue) => {
    console.log("selectedSpecies changed to:", newSpeciesValue);

    if (newSpeciesValue) {
      // Find the species in the available list and store its name
      const speciesItem = props.availableSpecies.find(s => s.value === newSpeciesValue);
      if (speciesItem) {
        selectedSpeciesName.value = speciesItem.title;
        console.log("Stored species name:", selectedSpeciesName.value);
      } else {
        console.log("Species not found in availableSpecies, keeping existing name:", selectedSpeciesName.value);
      }
    } else {
      selectedSpeciesName.value = null;
      console.log("Cleared species name");
    }
  }
);
</script>

<template>
  <v-card class="page-controls v-theme--mfnLight">
    <v-card-title class="pb-0">
      <h3>Analysis Parameters</h3>
    </v-card-title>
    <v-card-text>

      <!-- Classifier/Model Dropdown -->
      <div class="control-row horizontal align-inputs">
        <label for="model-select" class="label-inline text-right">Classifier</label>
        <v-select
          id="model-select"
          v-model="selectedModel"
          :items="models"
          item-title="title"
          item-value="id"
          return-object
          density="compact"
          @update:model-value="updateSelection"
          class="inline-select"
        ></v-select>
      </div>

      <!-- Site Lists Container -->
      <div class="site-lists-container">
        <!-- Available Sites List -->
        <div class="site-list">
          <label>Sites ({{ availableSitesList.length }})</label>
          <div class="site-list-scroll">
            <v-list density="compact" class="site-list-items">
              <v-list-item
                v-for="site in availableSitesList"
                :key="site.value"
                :value="site"
                @click="selectSite(site)"
                class="site-list-item"
              >
                {{ site.title }}
              </v-list-item>
              <v-list-item v-if="availableSitesList.length === 0">
                <v-list-item-title class="text-grey">No sites available</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </div>

        <!-- Selected Sites List -->
        <div class="site-list">
          <label>Selected (only 1 for now)</label>
          <div class="site-list-scroll">
            <v-list density="compact" class="site-list-items">
              <v-list-item
                v-for="site in selectedSites"
                :key="site.value"
                :value="site"
                @click="deselectSite(site)"
                class="site-list-item"
              >
                {{ site.title }}
                <template v-slot:append>
                  <v-icon color="error" size="small">mdi-close</v-icon>
                </template>
              </v-list-item>
              <v-list-item v-if="selectedSites.length === 0">
                <v-list-item-title class="text-grey">No sites selected</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </div>
      </div>

      <!-- Year Selector -->
      <div class="control-row horizontal align-inputs">
        <label for="year-select" class="label-inline text-right">Year</label>
        <v-select
          id="year-select"
          v-model="selectedYear"
          :items="years"
          density="compact"
          @update:model-value="updateSelection"
          class="inline-select"
          clearable
        ></v-select>
      </div>

      <!-- Species Selector -->
      <div class="control-row horizontal align-inputs">
        <label for="species-select" class="label-inline text-right">Species</label>
        <v-select
          id="species-select"
          v-model="selectedSpecies"
          :items="species"
          density="compact"
          @update:model-value="debouncedUpdateSpecies"
          class="inline-select species-select"
          item-class="species-item"
          clearable
          :disabled="hasOnlyPlaceholder"
          hide-details
        ></v-select>
        <!-- Display the appropriate message -->
        <div v-if="hasOnlyPlaceholder" class="custom-message">
          {{ placeholderMessage }}
        </div>
        <div v-else-if="speciesCountMessage" class="custom-message">
          {{ speciesCountMessage }}
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.page-controls {
  padding: 0;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.v-card-title {
  padding-bottom: 1em!important;
}

.v-card-text {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.site-lists-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.site-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.site-list-scroll {
  height: 22em;
  overflow-y: auto;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.02);
}

.site-list-items {
  background-color: transparent;
}

.site-list-item {
  cursor: pointer;
}

label {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}

/* Special styling for the light theme */
.v-theme--mfnLight {
  background-color: #ffffff;
  color: rgba(0, 0, 0, 0.87);
}

.v-theme--mfnLight .v-card-title {
  color: #2c3e50;
}

.v-theme--mfnLight .v-list {
  background-color: transparent;
}

.v-theme--mfnLight .v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.v-theme--mfnLight .site-list-scroll {
  background-color: #f5f5f5;
}

/* For horizontal layout controls (label + input on same line) */
.control-row.horizontal {
  flex-direction: row;
  align-items: center;
}

.control-row.horizontal .v-text-field {
  margin-top: 0;
  margin-bottom: 0;
}

.label-inline {
  margin-right: 1rem;
  margin-bottom: 0;
  min-width: 7em;
}

.inline-select {
  flex: 1;
}

/* Style for species select with italic selected value */
.species-select :deep(.v-field__input) {
  font-style: italic;
}

/* For specific styling of menu items if needed */
:deep(.species-item) {
  font-style: normal; /* Normal text for dropdown items */
}

:deep(.species-item.v-list-item--active) {
  font-style: italic; /* Italic for the active item in the dropdown */
}

/* Threshold input styling */
.threshold-input {
  width: 7em;
  max-width: 7em;
  flex-shrink: 0;
}

.threshold-input :deep(input) {
  text-align: center;
}

/* Alignment for the inputs */
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
  padding-right: 1em;
}

/* Input with hint on same line */
.input-with-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hint-text {
  color: rgba(0, 0, 0, 0.6);
  font-size: 0.75rem;
  white-space: nowrap;
}
.select-with-message {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
}
.custom-message {
  font-size: 0.75rem;
  padding-top: 4px;
  color: rgba(0, 0, 0, 0.7);
  font-weight: normal;
  line-height: 1.2;
  width: 40em;
  margin-left: 9em;
}
</style>