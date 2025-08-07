<script setup lang="ts">
import type { ModelInferenceResult } from "#gql/default";
import { watch } from "vue";

const props = defineProps<{
  recordId: number;
  confidence: number;
}>();
const emit = defineEmits(["update:results"]);

// Filter items with confidence >= 0.7
const baseSearch = computed(() => ({
  record_id: { _eq: props.recordId },
  confidence: { _gte: props.confidence }
}));

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
    search: baseSearch.value,
    sortBy: [{ key: "start_time", order: "asc" }],
    itemsPerPage: 100 
  }
});

watch(items, (val) => { console.log("items", val); });
watch(items, (val) => {
  emit("update:results", val);
}, { immediate: true });

const config = useRuntimeConfig();
const headers = [
  { title: "", key: "actions", align: "end", sortable: false, search: false },
//  { title: "ID", key: "id", align: "end", sortable: false, search: false },
  { title: "Start time", key: "start_time", align: "end", sortable: true, search: false },
  { title: "End time", key: "end_time", align: "end", sortable: true, search: false },
  { title: "Model ID", key: "model_id", align: "end", sortable: true, search:false  },
  { title: "(Model)", key: "model.name", align: "start", sortable: false, search: false },
  { title: "(Label)", key: "label.name", align: "start", sortable: false, search: false },
  { title: "Confidence", key: "confidence", align: "end", sortable: true, search: false }
] as const;

/************************
 * 
 * Model Filtering Logic
 * 
 ************************/

// Reactive reference for the currently selected model ID
const selectedModel = ref<number | null>(null);

/**
 * Model Filter Integration
 * Uses the useModelFilter composable to get available models for the dropdown
 * This provides a consistent way to access model data across the application
 */
const modelsFilter = useModelFilter({});

/**
 * Computed property to transform model data for v-select component
 * Converts raw model objects into the format expected by Vuetify's v-select
 * 
 * Format: {title: "display text", value: "option value"}
 * Display shows: "model_name (ID: model_id)" (e.g., "Bird Detection Model (ID: 123)")
 */
const models = computed(() => {
  // Return empty array if no data available
  if (!modelsFilter.data.value) return [];
  
  // Transform each model into dropdown option format
  return modelsFilter.data.value.map(model => ({
    title: `${model.name} (ID: ${model.id})`,  // Display format: "Name (ID: 123)"
    value: model.id                            // Value used for filtering
  }));
});

/**
 * Watch for model selection changes and apply filter
 * When user selects a model from the dropdown, automatically filter results
 * When selection is cleared, remove the model filter
 * 
 * Uses GraphQL-style filter syntax: {model_id: {_eq: modelId}}
 */
watch(selectedModel, (newModelId) => {
  if (newModelId) {
    // Apply model filter when model is selected
    console.log('Model selected:', newModelId);
    handleSearch({
      model_id: { _eq: newModelId }
    });
  } else {
    // Clear model filter when selection is cleared
    handleSearch({
      model_id: { _eq: undefined }
    });
  }
});

/************************
 * 
 * Download Inference Results Logic
 * 
 ************************/

// Track inference results for download functionality
const inferenceResults = ref([]);

// Watch items to update inferenceResults
watch(items, (newItems) => {
  if (newItems) {
    inferenceResults.value = newItems;
  }
}, { immediate: true });

/**
 * Downloads inference results as CSV file
 * Filters results by confidence threshold and formats data for CSV export
 */
function downloadInferenceCsv() {
  if (!inferenceResults.value || inferenceResults.value.length === 0) {
    console.warn('No inference results to download');
    return;
  }

  // Filter results by confidence threshold
  const filteredResults = inferenceResults.value.filter(result => 
    result.confidence >= props.confidence
  );

  if (filteredResults.length === 0) {
    console.warn(`No results found with confidence >= ${props.confidence}`);
    return;
  }

  // Convert to CSV format
  const csvHeaders = [
    'ID',
    'Start Time',
    'End Time', 
    'Model ID',
    'Model Name',
    'Label Name',
    'Confidence',
    'Record ID'
  ];

  const csvRows = filteredResults.map(result => [
    result.id,
    result.start_time,
    result.end_time,
    result.model_id,
    result.model?.name || 'N/A',
    result.label?.name || 'N/A',
    result.confidence,
    result.record_id
  ]);

  // Create CSV content
  const csvContent = [
    csvHeaders.join(','),
    ...csvRows.map(row => row.map(field => 
      typeof field === 'string' && field.includes(',') 
        ? `"${field}"` 
        : field
    ).join(','))
  ].join('\n');

  // Create and trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `inference_results_record_${props.recordId}_confidence_${props.confidence}.csv`);
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
      
      <!-- Model Dropdown -->
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
          Download Inference Results >= {{ confidence }}
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
            :items="[10, 25, 50, 100, 200, 500, 1000]"
            variant="outlined"
            density="compact"
            style="min-width: 100px;"
            hide-details
          />
          
          <!-- Page navigation -->
          <span class="text-caption mx-3">
            {{ ((page - 1) * itemsPerPage) + 1 }}-{{ Math.min(page * itemsPerPage, totalItems) }} of {{ totalItems }}
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

    <!-- <audio controls autoplay :src="source"></audio> -->
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
</style>