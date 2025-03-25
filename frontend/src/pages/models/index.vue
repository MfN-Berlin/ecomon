<script setup lang="ts">
definePageMeta({ layout: "submenu" });

const {
  page,
  itemsPerPage,
  sortBy,
  items,
  totalItems,
  isLoading: loading,
  handleReset,
  handleSearch
} = useModelPagniated();

const headers = [
  { title: "id", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "name", key: "name", align: "end", search: { operator: "_like", type: "text" } },
  { title: "remarks", key: "remarks", align: "end", search: { operator: "_like", type: "text" } },
  {
    title: "additional_docker_arguments",
    key: "additional_docker_arguments",
    align: "end",
    search: { operator: "_like", type: "text" }
  },
  {
    title: "additional_model_arguments",
    key: "additional_model_arguments",
    align: "end",
    search: { operator: "_like", type: "text" }
  },
  {
    title: "segment_duration",
    key: "segment_duration",
    align: "end",
    search: { operator: "_eq", type: "number" }
  },
  { title: "step_duration", key: "step_duration", align: "end", search: { operator: "_eq", type: "number" } }
] as const;
</script>

<template>
  <v-container>
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="items"
      :items-length="totalItems"
      :loading="loading"
      item-value="name"
    >
      <template v-slot:thead>
        <BaseTableSearchBar :headers="headers" @update:key="handleSearch" @update:reset="handleReset" />
      </template>
    </v-data-table-server>
  </v-container>
</template>
