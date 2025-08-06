<script setup lang="ts">
import type { Record } from "#gql/default";
import DataDirectoryBrowser from "~/components/sites/DataDirectoryBrowser.vue";

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

// Add state for the directory browser
const showDirectoryBrowser = ref(false);

// Extract the pagination options into a reusable constant
const paginationOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
  { value: 100, title: '100' },
];

const headers = [
  //{ title: "", key: "actions", align: "end", sortable: false, search: false },
  // { title: "Record Id", key: "id", align: "end", search: false },
  // search works on this object, because it exists in the record table (as site_id next to the nested object site {id ...})
  { title: "Site Id", key: "site_id", align: "start", sortable: true, search: false},
  // search is not possible on this field because it is a nested object
  { title: "(Site)", key: "site.name", align: "start", sortable: false, search: false },
  // commented out as filepath also includes filename
  // { title: "filename", key: "filename", align: "end", search: { operator: "_like", type: "text" } },


  // { title: "Record Type", key: "record_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Record Status", key: "record_status", align: "end", search: { operator: "_like", type: "text" } },
  { title: "File Path", key: "filepath", align: "start", search: { operator: "_like", type: "text" } },  // changed alignment to start for better readability
  // { title: "Date & Time", key: "record_datetime", align: "start", search: { operator: "_gte", type: "datetime" } }, // changed alignment to start for better readability
  { title: "Date & Time", key: "record_datetime", align: "start", search: false }, // changed alignment to start for better readability
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

function selectDirectory() {
  showDirectoryBrowser.value = true;
}

function handleSubmit(path: string[]) {
  console.log("submit", path);
  // Close the directory browser
  showDirectoryBrowser.value = false;
}

// Handle directory selection - using the correct format
function onDirectorySelected(directories: string[]) {
  console.log('Raw directories parameter:', directories);
  
  if (Array.isArray(directories) && directories.length > 0) {
    let selectedDirectory = directories[0];
    console.log('Selected directory:', selectedDirectory);
    
    if (selectedDirectory && selectedDirectory.trim() !== '') {
      console.log('Applying directory filter:', selectedDirectory);
      
      // Use the same format as your date search (direct object format)
      handleSearch({
        filepath: { _like: `%${selectedDirectory}%` }
      });
      
    } else {
      console.log('Selected directory is empty or invalid');
    }
  } else {
    console.log('No valid directories selected or invalid format');
  }
  
  showDirectoryBrowser.value = false;
}  

function onDirectoryBrowserClosed() {
  showDirectoryBrowser.value = false;
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
      :items-per-page-options="paginationOptions"
      >
      <!-- Add a top section with filters and pagination -->
      <template v-slot:top>
        <v-row align="center" class="pa-2" no-gutters>
          <!-- Filter input group on the left -->
          <v-col cols="auto">
            <v-card class="pa-3 mr-4" variant="outlined" color="primary">
              <v-card-title class="text-subtitle-2 pa-0 mb-2">Quick Filters</v-card-title>
              <v-row no-gutters>
                <v-col cols="auto" class="mr-3">
                  <v-btn
                    variant="outlined"
                    color="primary"
                    prepend-icon="mdi-folder-open"
                    style="min-width: 200px;"
                    @click="selectDirectory"
                  >
                    Select directory
                  </v-btn>
                </v-col>
                <v-col cols="auto">
                  <v-text-field
                    label="Date"
                    type="datetime-local"
                    density="compact"
                    variant="outlined"
                    clearable
                    style="min-width: 200px;"
                    @update:model-value="
                      handleSearch({
                        record_datetime: { _gte: $event ? new Date($event).toISOString() : undefined }
                      })
                    "
                  />
                </v-col>
              </v-row>
            </v-card>
          </v-col>
          
          <!-- Spacer to push pagination to the right -->
          <v-spacer />
          
          <!-- Pagination on the right -->
          <v-col cols="auto">
            <v-data-table-footer
              v-model:items-per-page="itemsPerPage"
              v-model:page="page"
              :items-length="totalItems"
              :page-count="Math.ceil(totalItems / itemsPerPage)"
              :items-per-page-options="paginationOptions"
              show-current-page
            />
          </v-col>
        </v-row>
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

    <!-- DataDirectoryBrowser component -->
    <v-dialog v-model="showDirectoryBrowser" persistent max-width="500px">
      <DataDirectoryBrowser
        v-if="showDirectoryBrowser"
        :directories="[]" 
        @select="onDirectorySelected"
        @cancel="onDirectoryBrowserClosed"
      />
    </v-dialog>


</v-container>
</template>
