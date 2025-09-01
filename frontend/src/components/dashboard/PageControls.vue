<script setup>
import { ref, computed, watch } from 'vue';

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
    default: () => ['2023', '2024', '2025']
  },
  availableSpecies: {
    type: Array,
    default: () => ['Strix aluco']
  }
});

// Add this right after props definition
watch(() => props.availableSites, (newSites) => {
  console.log("availableSites props changed:", newSites);
  console.log("Type:", typeof newSites);
  console.log("Is Array?", Array.isArray(newSites));
  console.log("Length:", newSites?.length);
  if (newSites && newSites.length > 0) {
    console.log("First item:", newSites[0]);
  }
}, { immediate: true });
const emit = defineEmits(['update:selection']);

// Initialize all reactive variables at the top
const selectedModel = ref(null);
const selectedSites = ref([]);
const selectedYear = ref(null);
const selectedSpecies = ref(null);

/***************
 * 
 * Selection update
 * 
****************/

// Function to emit selection updates
function updateSelection() {
  emit('update:selection', {
    model: selectedModel.value,
    sites: selectedSites.value,
    year: selectedYear.value,
    species: selectedSpecies.value
  });
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

// Watch for available models changes and select the first one
watch(
  () => props.availableModels,
  (newModels) => {
    if (newModels && newModels.length > 0 && !selectedModel.value) {
      // Select first model when data loads
      selectedModel.value = {
        title: newModels[0].name,
        value: newModels[0].id
      };
      
      // Emit initial selection
      updateSelection();
    }
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
  console.log("Computing availableSitesList with:", props.availableSites);
  
  if (!props.availableSites || !Array.isArray(props.availableSites)) {
    console.log("No available sites or not an array");
    return [];
  }
  
  // Filter out sites that are already selected
  const filtered = props.availableSites.filter(site => 
    !selectedSites.value.some(s => s.value === site.value)
  );
  
  console.log("Filtered sites:", filtered);
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
  selectedSites.value.push(site);
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

// Watch for available years changes and select the most recent one
watch(
  () => props.availableYears,
  (newYears) => {
    if (newYears && newYears.length > 0 && !selectedYear.value) {
      // Select the latest year (assuming years are sorted)
      selectedYear.value = newYears[newYears.length - 1];
      updateSelection();
    }
  },
  { immediate: true }
);

/***************
 * 
 * Species logic
 * 
****************/

const species = computed(() => props.availableSpecies);

watch(
  () => props.availableSpecies,
  (newSpecies) => {
    if (newSpecies && newSpecies.length > 0 && !selectedSpecies.value) {
      selectedSpecies.value = newSpecies[0];
      updateSelection();
    }
  },
  { immediate: true }
);


</script>

<template>
  <v-card class="page-controls v-theme--mfnLight">
    <v-card-title class="pb-0">
      <h3>Analysis Parameters</h3>
    </v-card-title>
    <v-card-text>
      <!-- Classifier/Model Dropdown -->
      <div class="control-row">
        <label for="model-select">Classifier</label>
        <v-select
          id="model-select"
          v-model="selectedModel"
          :items="models"
          item-title="title"
          item-value="id"
          return-object
          density="compact"
          @update:model-value="updateSelection"
        ></v-select>
      </div>

      <!-- Site Lists Container -->
      <div class="site-lists-container">
        <!-- Available Sites List -->
        <div class="site-list">
          <label>Sites ({{ availableSitesList.length }})</label>
          <div class="site-list-scroll">
            <v-list density="compact">
              <template v-if="availableSitesList.length > 0">
                <v-list-item
                  v-for="site in availableSitesList"
                  :key="site.value"
                  @click="selectSite(site)"
                >
                  {{ site.title }}
                </v-list-item>
              </template>
              <v-list-item v-else>
                <v-list-item-title class="text-grey">No sites available</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </div>

        <!-- Selected Sites List -->
        <div class="site-list">
          <label>Selected</label>
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
            </v-list>
          </div>
        </div>
      </div>

      <!-- Year Selector -->
      <div class="control-row horizontal">
        <label for="year-select" class="label-inline">Year</label>
        <v-select
          id="year-select"
          v-model="selectedYear"
          :items="years"
          density="compact"
          @update:model-value="updateSelection"
          class="inline-select"
        ></v-select>
      </div>

      <!-- Species Selector -->
      <div class="control-row horizontal">
        <label for="species-select" class="label-inline">Species</label>
        <v-select
          id="species-select"
          v-model="selectedSpecies"
          :items="species"
          density="compact"
          @update:model-value="updateSelection"
          class="inline-select species-select"
          item-class="species-item"
        ></v-select>
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
  padding-bottom: 0;
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

.label-inline {
  margin-right: 1rem;
  margin-bottom: 0;
  min-width: 60px;
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
</style>