<script setup>
import { ref, computed, watch, onMounted } from 'vue';
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
const speciesSearchInput = ref('');
let thresholdTimeoutId = null;

/*******************************************
 * Fetch ready sites from database
 ******************************************/

// Use the composable from workflowReports.ts
const { data: readySiteIds, pending, error, fetchReadySites } = useReadySites();

// Watch readySiteIds for changes
watch(readySiteIds, (newValue) => {
  console.log('🔍 readySiteIds changed:', newValue);
  console.log('   - Type:', typeof newValue);
  console.log('   - Is Array:', Array.isArray(newValue));
  console.log('   - Length:', newValue?.length);
}, { immediate: true });

// Watch pending state
watch(pending, (newValue) => {
  console.log('⏳ Pending state:', newValue);
});

// Watch error state
watch(error, (newValue) => {
  if (newValue) {
    console.error('❌ Error loading ready sites:', newValue);
  }
});

// Fetch ready sites when component mounts
onMounted(async () => {
  console.log('🚀 Component mounted, fetching ready sites...');
  await fetchReadySites();
  console.log('✅ Fetch complete. readySiteIds:', readySiteIds.value);
});

/******************
 * Models logic
 ******************/

// Read ready model IDs from environment (comma-separated ints). If none, enable all.
const envReadyModelIds = (import.meta.env?.VITE_READY_MODEL_IDS || '').trim();
const readyModelIds = ref([]); // was: ref<number[]>([])

const initReadyModelIds = () => {
  if (envReadyModelIds.length > 0) {
    readyModelIds.value = envReadyModelIds
      .split(',')
      .map(s => Number(s.trim()))
      .filter(n => Number.isFinite(n));
  } else {
    // No env var: mark all available models as ready
    readyModelIds.value = Array.isArray(props.availableModels)
      ? props.availableModels.map(m => m.id)
      : [];
  }
};

// Keep readyModelIds in sync when availableModels changes (for "enable all" case)
watch(
  () => props.availableModels,
  () => {
    if (!envReadyModelIds.length) {
      readyModelIds.value = Array.isArray(props.availableModels)
        ? props.availableModels.map(m => m.id)
        : [];
    }
  },
  { immediate: true }
);

onMounted(() => {
  initReadyModelIds();
});

// Models list with readiness
const models = computed(() => {
  return (props.availableModels || []).map(model => ({
    title: model.name,
    value: model.id,
    isReady: readyModelIds.value.includes(model.id)
  }));
});


/*****************
* Species logic
******************/
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
    species: selectedSpecies.value, // Preserve species selection
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


/***************
 *
 * Sites logic
 *
****************/

// Available sites (those not yet selected)
const availableSitesList = computed(() => {
  console.log('📋 Computing availableSitesList');
  console.log('   - readySiteIds.value:', readySiteIds.value);
  console.log('   - props.availableSites:', props.availableSites);

  if (!props.availableSites || !Array.isArray(props.availableSites)) {
    console.log("❌ No available sites or not an array");
    return [];
  }

  // Filter out sites that are already selected and add ready status
  const filtered = props.availableSites
    .filter(site => !selectedSites.value.some(s => s.value === site.value))
    .map(site => {
      const isReady = readySiteIds.value.includes(site.value);
      console.log(`   - Site ${site.value} (${site.title}): isReady = ${isReady}`);
      return {
        ...site,
        isReady
      };
    });

  console.log('   - Filtered sites count:', filtered.length);
  console.log('   - Ready sites count:', filtered.filter(s => s.isReady).length);

  return filtered;
});

// Watch for available sites changes to update available list
watch(
  () => props.availableSites,
  () => {
    // When sites list changes, we don't auto-select any
    // but we ensure the availableSitesList is updated
    // DON'T call updateSelection here to prevent clearing species
//    updateSelection();
  },
  { immediate: true }
);

// Function to select a site
function selectSite(site) {
  // Only allow selection if site is ready
  if (!site.isReady) {
    return;
  }
  selectedSites.value.push(site);  // Set to allow multiple selections
  // selectedSites.value = [site]; // Set to array with only the new site
  // updateSelection();
  // Call updateSelection but preserve the species
  emit('update:selection', {
    model: selectedModel.value,
    sites: selectedSites.value,
    year: selectedYear.value,
//    species: selectedSpecies.value, // Preserve species selection
    threshold: threshold.value
  });
}

// Function to deselect a site
function deselectSite(site) {
  selectedSites.value = selectedSites.value.filter(s => s.value !== site.value);
//  updateSelection();
  // Call updateSelection but preserve the species
  emit('update:selection', {
    model: selectedModel.value,
    sites: selectedSites.value,
    year: selectedYear.value,
    // Don't include species in the emit to preserve it
//    species: selectedSpecies.value, // Preserve species selection
    threshold: threshold.value
  });
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
//    updateSelection();
  },
  { immediate: true }
);

/***************
 *
 * Species logic
 *
****************/

// Get the filtered species list for the dropdown based on search input
const filteredSpecies = computed(() => {
  console.log("Computing filtered species list:");
  console.log("- speciesSearchInput:", speciesSearchInput.value);
  console.log("- selectedSpecies:", selectedSpecies.value);

  // If search input is less than 3 characters and no species is selected, return empty array
  if ((!speciesSearchInput.value || speciesSearchInput.value.length < 3) && !selectedSpecies.value) {
    console.log("-> Returning empty array (less than 3 chars and no selection)");
    return [];
  }

  let filtered = [];

  // Add all available species except placeholders
  if (!hasOnlyPlaceholder.value) {
    console.log("- Filtering available species...");
    filtered = props.availableSpecies.filter(item => {
      // console.log("  - Checking item:", item.title, "isPlaceholder:", item.isPlaceholder);
      if (item.isPlaceholder) return false;

      // If there's search input, filter by it
      if (speciesSearchInput.value && speciesSearchInput.value.length >= 3) {
        const matches = item.title.toLowerCase().includes(speciesSearchInput.value.toLowerCase());
        console.log("    -> Search match:", matches, "for search:", speciesSearchInput.value);
        return matches;
      }

      console.log("    -> Including (no search filter)");
      return true;
    });
  }

  // Ensure the currently selected species is included
  if (
    selectedSpecies.value &&
    !filtered.some(s => s.value === selectedSpecies.value)
  ) {
    const speciesName = getSpeciesName(selectedSpecies.value);
    filtered.push({
      value: selectedSpecies.value,
      title: speciesName
        ? `${speciesName} (not in list)`
        : `Species ${selectedSpecies.value} (not in list)`
    });
  }

  return filtered;
});

// Update the species computed property message
const speciesCountMessage = computed(() => {
  // Show message if not a placeholder and there are available species
  if (!hasOnlyPlaceholder.value && props.availableSpecies.length > 0) {
    const totalCount = props.availableSpecies.filter(s => !s.isPlaceholder).length;

    // If no search input or less than 3 characters, show total count
    if (!speciesSearchInput.value || speciesSearchInput.value.length < 3) {
      const message = `${totalCount} species available - type to search`;
      return message;
    }
    // If 3+ characters typed
    else if (speciesSearchInput.value.length >= 3) {
      const filteredCount = filteredSpecies.value.length;

      // If exactly 1 species matches, show no message
      if (filteredCount === 1) {
        return null;
      }

      // Otherwise show the filtered count
      const message = `${totalCount} species found`;
      return message;
    }
  }
  return null;
});

watch(
  () => props.availableSpecies,
  (newSpecies) => {
    console.log("availableSpecies changed:");
    console.log("- newSpecies length:", newSpecies.length);
    console.log("- selectedSpecies:", selectedSpecies.value);

    if (selectedSpecies.value) {
      // Check if the selected species exists in the new list
      const currentSpecies = newSpecies.find(s => s.value === selectedSpecies.value);
      if (currentSpecies) {
        console.log("Selected species is still valid:", currentSpecies.title);
        selectedSpeciesName.value = currentSpecies.title; // Update the name
      } else {
        console.log("Selected species not in new list, preserving selection");
        // Keep the species selected but mark it as not in the list
        const speciesName = getSpeciesName(selectedSpecies.value);
        selectedSpeciesName.value = speciesName
          ? `${speciesName}`
          : `Species ${selectedSpecies.value} (not in list)`;
      }
    } else if (hasOnlyPlaceholder.value) {
      console.log("Only placeholder available - clearing selection");
      selectedSpecies.value = null;
      selectedSpeciesName.value = null;
    }
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
          item-value="value"
          return-object
          density="compact"
          @update:model-value="updateSelection"
          class="inline-select"
        >
          <template v-slot:item="{ props, item }">
            <v-list-item
              v-bind="props"
              :disabled="!item.raw.isReady"
              :class="{ 'model-not-ready': !item.raw.isReady }"
            >
              <template v-slot:append v-if="!item.raw.isReady">
                <v-chip size="x-small" color="warning" variant="flat">Pending</v-chip>
              </template>
            </v-list-item>
          </template>
          <template v-slot:selection="{ item }">
            <span :class="{ 'text-grey': !item.raw.isReady }">
              {{ item.title }}
              <v-chip v-if="!item.raw.isReady" size="x-small" color="warning" variant="flat" class="ml-2">Pending</v-chip>
            </span>
          </template>
        </v-select>
      </div>

      <!-- Site Lists Container -->
      <div class="site-lists-container">
        <!-- Available Sites List -->
        <div class="site-list">
          <label>Sites available ({{ availableSitesList.length }})</label>
          <div class="site-list-scroll">
            <v-list density="compact" class="site-list-items">
              <v-list-item
                v-for="site in availableSitesList"
                :key="site.value"
                :value="site"
                @click="selectSite(site)"
                :class="['site-list-item', { 'site-not-ready': !site.isReady }]"
                :disabled="!site.isReady"
              >
                {{ site.title }}
                <template v-slot:append v-if="!site.isReady">
                  <v-chip size="x-small" color="warning" variant="flat">Pending</v-chip>
                </template>
              </v-list-item>
              <v-list-item v-if="availableSitesList.length === 0">
                <v-list-item-title class="text-grey">No sites available</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </div>

        <!-- Selected Sites List -->
        <div class="site-list">
          <label>Sites selected ({{ selectedSites.length }})</label>
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
        <div class="select-with-message">
          <v-autocomplete
            id="species-select"
            v-model="selectedSpecies"
            v-model:search="speciesSearchInput"
            :items="filteredSpecies"
            density="compact"
            @update:model-value="debouncedUpdateSpecies"
            class="inline-select species-select"
            item-class="species-item"
            clearable
            :disabled="hasOnlyPlaceholder"
            placeholder="Type at least 3 characters..."
            :no-filter="true"
          >
            <template v-slot:no-data>
              <v-list-item v-if="speciesSearchInput && speciesSearchInput.length < 3">
                <v-list-item-title class="text-grey">Type at least 3 characters to search</v-list-item-title>
              </v-list-item>
              <v-list-item v-else>
                <v-list-item-title class="text-grey"></v-list-item-title>
              </v-list-item>
            </template>
          </v-autocomplete>
          <!-- Reserve space for messages -->
          <div class="message-container">
            <div v-if="hasOnlyPlaceholder" class="custom-message" v-html="placeholderMessage"></div>
            <div v-else-if="speciesCountMessage" class="species-message success-message">
              {{ speciesCountMessage }}
            </div>
          </div>
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

.site-list-item.site-not-ready {
  cursor: not-allowed;
  opacity: 0.6;
}

.model-not-ready {
  opacity: 0.6;
  cursor: not-allowed;
}

.model-not-ready:hover {
  background-color: transparent !important;
}

.site-list-item.site-not-ready:hover {
  background-color: transparent !important;
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
/* Label column styling */
.label-col {
  width: 7em;
  min-width: 7em;
  padding-right: 1em;
}

.label-col .label-inline {
  padding-top: 0.5rem;
  display: block;
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
  grid-template-columns: 7em 1fr; /* Fixed label width and flexible input width */
  align-items: center; /* Aligns label and input vertically */
  gap: 0.75rem;
}

/* Right-align labels */
.text-right {
  text-align: right;
  margin-right: 0;
  padding-right: 1em;
  padding-top: 0.25em; /* Adjusts vertical alignment */
}

/* Select with message container */
.select-with-message {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* Message styling */
.species-message {
  font-size: 0.75rem;
  padding-top: 4px;
  padding-left: 12px;
  color: rgba(0, 0, 0, 0.6);
  font-style: italic;
  min-height: 18px; /* Prevents layout shift */
}

.success-message {
  color: #2e7d32;
  font-weight: 500;
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
/* Reserve space for messages to prevent layout shifts */
.message-container {
  min-height: 1.5rem; /* Adjust this value to match the height of your messages */
}

/* Styling for the species message */
.species-message {
  font-size: 0.75rem;
  padding-top: 4px;
  padding-left: 12px;
  color: rgba(0, 0, 0, 0.6);
  font-style: italic;
}

/* Styling for the success message */
.success-message {
  color: #2e7d32;
  font-weight: 500;
}

/* Styling for the placeholder message */
.custom-message {
  font-size: 0.75rem;
  padding-top: 4px;
  color: rgba(0, 0, 0, 0.7);
  font-weight: normal;
  line-height: 1.2;
}
/* Specific styling for the Species label */
label[for="species-select"] {
  margin-top: -3em;
}
</style>