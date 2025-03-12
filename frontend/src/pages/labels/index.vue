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
} = useLabelsPagniated();

const headers = [
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" }, width: 100 },
  { title: "Scientific name", key: "name", align: "end", search: { operator: "_like", type: "text" } },
  { title: "English", key: "english", align: "end", search: { operator: "_like", type: "text" } },
  { title: "German", key: "german", align: "end", search: { operator: "_like", type: "text" } },
  { title: "GBIF", key: "gbif", align: "end", search: { operator: "_like", type: "text" } },
  { title: "Class", key: "class", align: "end", search: { operator: "_like", type: "text" } },
  { title: "Order", key: "order", align: "end", search: { operator: "_like", type: "text" } }
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
