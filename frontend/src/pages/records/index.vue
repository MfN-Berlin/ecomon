<script setup lang="ts">
import type { Record } from "#gql/default";

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
} = useRecordsPagniated();

const config = useRuntimeConfig();
const headers = [
  { title: "", key: "actions", align: "end", sortable: false, search: false },
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "filename", key: "filename", align: "end", search: { operator: "_like", type: "text" } },
  { title: "filepath", key: "filepath", align: "end", search: { operator: "_like", type: "text" } },
  { title: "duration", key: "duration", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "channels", key: "channels", align: "end", search: { operator: "_like", type: "text" } },
  { title: "mime_type", key: "mime_type", align: "end", search: { operator: "_like", type: "text" } },
  { title: "record_datetime", key: "record_datetime", align: "end", search: false },
  { title: "sample_rate", key: "sample_rate", align: "end", search: { operator: "_eq", type: "number" } }
] as const;
</script>

<template>
  <v-container>
    <!-- <audio controls autoplay :src="source"></audio> -->
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
      <template #item.actions="{ item }: { item: Record }">
        <v-toolbar density="compact" color="surface">
          <app-play-button
            :src="`${config.public.API_BASE_URL}/static/files/${item.filepath}`"
            variant="text"
            size="small"
          />
          <nuxt-link :to="`/records/${item.id}`">
            <v-btn icon variant="text" size="small">
              <v-icon>mdi-pen</v-icon>
            </v-btn>
          </nuxt-link>
        </v-toolbar>
      </template>
    </v-data-table-server>
  </v-container>
</template>
