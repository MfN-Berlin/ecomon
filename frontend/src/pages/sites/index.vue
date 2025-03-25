<script setup lang="ts">
import type { GetSitesPagniatedQuery } from "#gql";

type Site = GetSitesPagniatedQuery["items"][number];
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
} = useSitePagniated();

const headers = [
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "name", key: "name", align: "end", search: { operator: "_like", type: "text" } },
  { title: "prefix", key: "prefix", align: "end", search: { operator: "_like", type: "text" } },
  {
    title: "record_regime_pause_duration",
    key: "record_regime_pause_duration",
    align: "end",
    search: false
  },
  {
    title: "record_regime_recording_duration",
    key: "record_regime_recording_duration",
    align: "end",
    search: false
  },
  { title: "sample_rate", key: "sample_rate", align: "end", search: { operator: "_eq", type: "number" } }
] as const;

const markers = computed(() => {
  return (items.value as Site[])
    .filter((item) => item.location.lat && item.location.long)
    .map((item) => ({
      id: item.id,
      name: item.name,
      lat: item.location.lat,
      long: item.location.long,
      to: `/sites/${item.id}`
    }));
});
</script>

<template>
  <v-container>
    <BaseMap :markers="markers" />
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
      </template>
    </v-data-table-server>
  </v-container>
</template>
