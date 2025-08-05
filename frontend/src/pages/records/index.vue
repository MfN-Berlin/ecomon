<script setup lang="ts">
import type { Record } from "#gql/default";

definePageMeta({ layout: "full-width" });

const {
  page,
  itemsPerPage,
  sortBy,
  items,
  totalItems,
  isLoading: loading,
  handleReset,
  handleSearch
} = useRecordsPaginated();

const config = useRuntimeConfig();
const headers = [
  //{ title: "", key: "actions", align: "end", sortable: false, search: false },
  // { title: "Record Id", key: "id", align: "end", search: false },
  // search works on this object, because it exists in the record table (as site_id next to the nested object site {id ...})
  { title: "Site Id", key: "site_id", align: "start", sortable: true, search: false},
  // search is not possible on this field because it is a nested object
  { title: "(Site)", key: "site.name", align: "start", sortable: false, search: false },
  // commented out as filepath also includes filename
  // { title: "filename", key: "filename", align: "end", search: { operator: "_like", type: "text" } },

  // { title: "Date & Time", key: "record_datetime", align: "start", search: { operator: "_gte", type: "datetime" } }, // changed alignment to start for better readability
  { title: "Date & Time", key: "record_datetime", align: "start", search: false }, // changed alignment to start for better readability

  // { title: "Record Type", key: "record_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Record Status", key: "record_status", align: "end", search: { operator: "_like", type: "text" } },
  { title: "File Path", key: "filepath", align: "start", search: { operator: "_like", type: "text" } },  // changed alignment to start for better readability
  // { title: "File Size", key: "file_size", align: "end", search: { operator: "_eq", type: "number" } },
  // { title: "File Type", key: "file_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Duration", key: "duration", align: "end", search: { operator: "_eq", type: "number" } },
  // { title: "Channels", key: "channels", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Mime Type", key: "mime_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Sample Rate", key: "sample_rate", align: "end", search: { operator: "_eq", type: "number" } },
] as const;

function goToItem(id) {
  window.open(`records/${id}`, '_blank')
}
function getNested(obj, key) {
  return key.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
}
</script>

<style scoped>
tr:hover {
  background-color: #f0f8ff;
  cursor: pointer;
}
/* Style for sortable headers */
.v-data-table-header__sortable {
  background-color: #f0f0f0; /* Light grey background */
  font-weight: 800!important; /* Bold text */
  cursor: pointer; /* Change cursor to pointer */
}

/* Optional: Style for the sort icon */
.v-data-table-header__sort-icon {
  color: #333; /* Dark grey sort icon */
}
/*
  This CSS targets the "Items per page" dropdown in the data table's
  footer and gives it a minimum width to prevent text truncation.
*/
:deep(.v-data-table-footer__items-per-page .v-select) {
  min-width: 100px;
}
</style>

<template>
  <v-container fluid>
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
      <!-- Add a top pagination component -->
      <template v-slot:top>
        <v-data-table-footer
          v-model:items-per-page="itemsPerPage"
          v-model:page="page"
          :items-length="totalItems"
          :page-count="Math.ceil(totalItems / itemsPerPage)"
          show-current-page
        />
      </template>

      <template v-slot:thead>
        <CommonTableSearchBar :headers="headers" @update:key="handleSearch" @update:reset="handleReset" />
      </template>
      <template #item="{ item }">
        <tr @click="goToItem(item.id)" style="cursor: pointer;">
          <td v-for="header in headers" :key="header.key">
            <!--{{ item[header.key] }}-->
            {{ getNested(item, header.key) }}
          </td>
        </tr>
      </template>
    </v-data-table-server>
  </v-container>
</template>
