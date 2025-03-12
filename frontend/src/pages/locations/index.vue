<script setup lang="ts">
import type { LocationFragment } from "#gql";

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
} = useLocationPagniated();

const headers = [
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "name", key: "name", align: "end", search: { operator: "_like", type: "text" } },
  { title: "lat", key: "lat", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "long", key: "long", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "remarks", key: "remarks", align: "end", search: { operator: "_like", type: "text" } }
] as const;

const markers = computed(() => {
  return (items.value as LocationFragment[])
    .filter((item) => item.lat && item.long)
    .map((item) => ({
      id: item.id,
      name: item.name,
      lat: item.lat,
      long: item.long,
      to: `/locations/${item.id}`
    }));
});
</script>

<template>
  <v-container>
    <BaseMap :markers />
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="items"
      :items-length="totalItems"
      :loading="loading"
      item-value="name"
      :animate="true"
    >
      <template v-slot:thead>
        <BaseTableSearchBar :headers="headers" @update:key="handleSearch" @update:reset="handleReset" />
      </template> </v-data-table-server
  ></v-container>
</template>
