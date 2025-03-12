<script setup lang="ts">
definePageMeta({ layout: "default" });

const {
  page,
  itemsPerPage,
  sortBy,
  items,
  totalItems,
  isLoading: loading,
  handleReset,
  handleSearch
} = useGetJobsPagniated({
  startValues: {
    page: 1,
    itemsPerPage: 10,
    sortBy: [{ key: "id", order: "desc" }],
    search: {}
  }
});
const headers = [
  { title: "id", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "status", key: "status", align: "end", search: false },
  { title: "topic", key: "topic", align: "end", search: { operator: "_eq", type: "text" } },
  { title: "payload", key: "payload", align: "end", search: false },
  { title: "progress", key: "progress", align: "end", search: false },
  { title: "error", key: "error", align: "end", search: false },
  { title: "updated_at", key: "updated_at", align: "end", search: false },
  { title: "created_at", key: "created_at", align: "end", search: false }
] as const;

const { $activeJobs } = useNuxtApp();
</script>

<template>
  <v-container>
    <h2>Active jobs</h2>

    <v-data-table :headers="headers" :items="$activeJobs?.jobs" class="min-height-100"></v-data-table>

    <h2>Finished jobs</h2>
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
