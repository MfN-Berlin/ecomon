<script setup lang="ts">
import type { ModelInferenceResult } from "#gql/default";
import { watch } from "vue";

const props = defineProps<{
  recordId: number;
}>();

const emit = defineEmits(["update:results"]);

const baseSearch = computed(() => ({
  record_id: { _eq: props.recordId },
  confidence: { _gte: 0.7 }
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
} = useRecordModelInferenceResultsPagniated({
  startValues: {
    search: baseSearch.value,
    sortBy: [{ key: "start_time", order: "asc" }],
//    itemsPerPage: 100 
  }
});

// Filter items with confidence >= 0.7 for display and emit
//const filteredItems = computed(() =>
//  (items.value || []).filter(r => Number(r.confidence) >= 0.0)
//);
// const filteredItems = computed(() => items.value || []);
watch(items, (val) => { console.log("items", val); });
watch(items, (val) => {
  emit("update:results", val);
}, { immediate: true });

const config = useRuntimeConfig();
const headers = [
  { title: "", key: "actions", align: "end", sortable: false, search: false },
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "Model", key: "model.name", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "Label", key: "label.name", align: "end", search: { operator: "_eq", type: "text" } },
  { title: "Start time", key: "start_time", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "End time", key: "end_time", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "Confidence", key: "confidence", align: "end", search: { operator: "_eq", type: "number" } }
] as const;

</script>

<template>
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
  </v-data-table-server>
</template>
