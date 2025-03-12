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
} = useSetsPagniated();

const headers = [
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "name", key: "name", align: "end", search: { operator: "_like", type: "text" } },
  {
    title: "sites",
    key: "sets_sites_selections_aggregate.aggregate.count",
    align: "end",
    search: { operator: "_eq", type: "number" }
  },
  {
    title: "start_date",
    key: "set_information.start_date",
    align: "end",
    search: false
  },
  {
    title: "end_date",
    key: "set_information.end_date",
    align: "end",
    search: false
  },
  { title: "remarks", key: "remarks", align: "end", search: { operator: "_like", type: "text" } }
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
