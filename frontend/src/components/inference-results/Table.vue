<script setup lang="ts">
import type { ModelInferenceResult } from "#gql/default";
import { ref, computed, watch } from "vue";

const props = defineProps<{
  recordId: number;
  confidence: number;
}>();
const emit = defineEmits(["update:results"]);

/******************************
 *
 * Filtering Logic
 *
 ******************************/
// --- Filter State ---
const selectedModel = ref<number | null>(null);
const filterConfidence = ref(0.5);
const filterSpecies = ref('');

// --- Debouncing ---
const debouncedFilterConfidence = ref(filterConfidence.value);
const debouncedFilterSpecies = ref(filterSpecies.value);

const confidenceDebounceTimer = ref<number | undefined>(undefined);
watch(filterConfidence, (newValue) => {
  if (confidenceDebounceTimer.value) {
    clearTimeout(confidenceDebounceTimer.value);
  }
  confidenceDebounceTimer.value = setTimeout(() => {
    debouncedFilterConfidence.value = newValue;
  }, 400);
});

const speciesDebounceTimer = ref<number | undefined>(undefined);
watch(filterSpecies, (newValue) => {
  if (speciesDebounceTimer.value) {
    clearTimeout(speciesDebounceTimer.value);
  }
  speciesDebounceTimer.value = setTimeout(() => {
    debouncedFilterSpecies.value = newValue;
  }, 400);
});

// --- Model Autocomplete ---
const modelsFilter = useModelFilter({});
const models = computed(() => {
  if (!modelsFilter.data.value) return [];
  return modelsFilter.data.value.map(model => ({
    title: `${model.name} (ID: ${model.id})`,
    value: model.id
  }));
});

// --- Labels Autocomplete ---
// --- Labels Autocomplete ---
const labelsFilter = useLabelsPaginated({
  startValues: {
    itemsPerPage: 100000, // Get a large number of labels
    search: {}
  }
});

// Trigger the query to fetch all labels
onMounted(() => {
  // No need to call onSearchTermChanged for paginated query
});

const labels = computed(() => {
  console.log("Labels computed - raw data:", labelsFilter.items.value);
  console.log("Labels isLoading:", labelsFilter.isLoading.value);
  if (!labelsFilter.items.value) return [];
  const mappedLabels = labelsFilter.items.value.map(label => label.name);
  console.log("Mapped labels:", mappedLabels);
  return mappedLabels;
});
// Create species items for autocomplete
const speciesItems = computed(() => {
  console.log("Species items computed, labels:", labels.value);
  return labels.value;
});

/************************
 * 
 * Data Table Logic
 * 
 ************************/

const baseSearch = computed(() => {
  const search: any = {
    record_id: { _eq: props.recordId },
    confidence: { _gte: debouncedFilterConfidence.value }
  };
  
  if (selectedModel.value) {
    search.model_id = { _eq: selectedModel.value };
  }
  
  if (debouncedFilterSpecies.value) {
    search.label = { name: { _ilike: `%${debouncedFilterSpecies.value}%` } };
  }

  return search;
});

const {
  page,
  itemsPerPage,
  sortBy,
  items,
  totalItems,
  isLoading: loading,
  handleReset,
  handleSearch
} = useRecordModelInferenceResultsPaginated({
  startValues: {
    search: baseSearch,
    sortBy: [{ key: "start_time", order: "asc" }],
    itemsPerPage: 1000000
  }
});

watch(items, (val) => {
  emit("update:results", val);
}, { immediate: true });

const config = useRuntimeConfig();
const headers = [
  { title: "", key: "actions", align: "end", sortable: false, search: false },
  { title: "Start time (s)", key: "start_time", align: "end", sortable: true, search: false },
  { title: "End time (s)", key: "end_time", align: "end", sortable: true, search: false },
  { title: "Model", key: "model.name", align: "start", sortable: false, search: false },
  { title: "Species", key: "label.name", align: "start", sortable: false, search: false },
  { title: "Confidence", key: "confidence", align: "end", sortable: true, search: false }
] as const;

const itemsPerPageOptions = [
  { title: '10', value: 10 },
  { title: '25', value: 25 },
  { title: '50', value: 50 },
  { title: '100', value: 100 },
  { title: 'All', value: 1000000 }
];

/************************************
 * 
 * Download Inference Results Logic
 * 
 ***********************************/

const inferenceResults = ref<ModelInferenceResult[]>([]);
watch(items, (newItems) => {
  if (newItems) {
    inferenceResults.value = newItems as ModelInferenceResult[];
  }
}, { immediate: true });

const downloadableResults = computed(() => {
  return inferenceResults.value.filter(result => 
    result.confidence >= filterConfidence.value
  );
});

function downloadInferenceCsv() {
  const filteredResults = downloadableResults.value;
  if (filteredResults.length === 0) {
    console.warn('No inference results to download');
    return;
  }

  const csvHeaders = [
    'ID', 'Start Time', 'End Time', 'Model ID', 'Model Name', 
    'Label Name', 'Confidence', 'Record ID'
  ];

  const csvRows = filteredResults.map(result => [
    result.id, result.start_time, result.end_time, result.model_id,
    result.model?.name || 'N/A', result.label?.name || 'N/A',
    result.confidence, result.record_id
  ]);

  const csvContent = [
    csvHeaders.join(','),
    ...csvRows.map(row => row.map(field => 
      typeof field === 'string' && field.includes(',') ? `"${field}"` : field
    ).join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `inference_results_record_${props.recordId}_confidence_${filterConfidence.value}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
</script>

<template>
  <div>
    <!-- Filter Controls Card -->
    <v-card class="pa-3 mb-4" variant="outlined" color="primary">
      <v-card-title class="text-subtitle-2 pa-0 mb-2">Quick Filters</v-card-title>
      <!-- Filter Controls Row -->
      <v-row no-gutters class="align-center">
        <!-- Model Dropdown -->
        <v-col class="pr-2">
          <v-select
            v-model="selectedModel"
            label="Select model"
            :items="models"
            variant="outlined"
            density="compact"
            clearable
            item-title="title"
            item-value="value"
            prepend-inner-icon="mdi-brain"
          />
        </v-col>
        <!-- Species Input -->
        <v-col class="pr-2">
          <v-autocomplete
            v-model="filterSpecies"
            :items="speciesItems"
            label="Filter by species"
            variant="outlined"
            density="compact"
            clearable
            prepend-inner-icon="mdi-bird"
            :loading="labelsFilter.isLoading.value"
          />
        </v-col>
        <!-- Confidence Input -->
        <v-col cols="2">
          <v-text-field
            v-model.number="filterConfidence"
            label="Filter by confidence"
            type="number"
            min="0.1"
            max="1.0"
            step="0.001"
            variant="outlined"
            density="compact"
            prepend-inner-icon="mdi-target"
          />
        </v-col>
      </v-row>
    </v-card>

    <!-- Top Controls Row -->
    <v-row align="center" class="pa-2 mb-2" no-gutters>
      <!-- Download Button -->
      <v-col cols="auto">
        <v-btn
          color="primary"
          prepend-icon="mdi-download"
          @click="downloadInferenceCsv"
          :disabled="!inferenceResults.length"
        >
          Download {{ downloadableResults.length }} Inference Results
        </v-btn>
      </v-col>

      <!-- Spacer to push pagination to the right -->
      <v-spacer />
      
      <!-- Top Pagination Controls -->
      <v-col cols="auto">
        <div class="d-flex align-center">
          <!-- Items per page selector -->
          <span class="text-caption mr-2">Items per page:</span>
          <v-select
            v-model="itemsPerPage"
            :items="itemsPerPageOptions"
            variant="outlined"
            density="compact"
            style="min-width: 100px;"
            hide-details
          />
          
          <!-- Page navigation -->
          <span class="text-caption mx-3">
            {{ itemsPerPage === 1000000 ? `1-${totalItems} of ${totalItems}` : `${((page - 1) * itemsPerPage) + 1}-${Math.min(page * itemsPerPage, totalItems)} of ${totalItems}` }}
          </span>
          
          <v-btn
            icon="mdi-chevron-left"
            variant="text"
            density="compact"
            :disabled="page <= 1"
            @click="page--"
          />
          <v-btn
            icon="mdi-chevron-right"
            variant="text"
            density="compact"
            :disabled="page >= Math.ceil(totalItems / itemsPerPage)"
            @click="page++"
          />
        </div>
      </v-col>
    </v-row>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="items"
      :items-length="totalItems"
      :loading="loading"
      item-value="id"
      :recordId="props.recordId"
      :items-per-page-options="itemsPerPageOptions"
    >
      <template v-slot:thead>
        <CommonTableSearchBar :headers="headers" @update:key="handleSearch" @update:reset="handleReset" />
      </template>
      <template #item.actions="{ item }: { item: ModelInferenceResult }">
        <v-toolbar density="compact" color="surface">
          <app-play-button
            :src="`${config.public.API_BASE_URL}/files/records/${item.record_id}/inference-result/${item.id}/flac?padding_ms=5000`"
            variant="text"
            size="small"
          />
        </v-toolbar>
      </template>
      <!-- Custom template for label.name -->
      <template #item.label.name="{ item }">
        <em v-if="item.label">{{ item.label.name }}</em>
        <span v-else>N/A</span>
      </template>
    </v-data-table-server>
  </div>
</template>

<style scoped>
/* Target the v-select within the v-data-table-footer */
/* Use :deep() to penetrate component encapsulation */
:deep(.v-data-table-footer__items-per-page > .v-select) {
  min-width: 100px;  /* Adjust this value to make it wider */
}
/* Make sortable headers bold */
:deep(.v-data-table__th--sortable) {
  font-weight: bold!important;
}
</style>