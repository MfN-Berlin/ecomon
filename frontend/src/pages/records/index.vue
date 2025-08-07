<script setup lang="ts">
/**
 * Records Index Page
 * 
 * This page displays a paginated, sortable, and filterable table of audio records.
 * Features include:
 * - Site-based filtering via dropdown
 * - Server-side pagination with configurable page sizes
 * - Column sorting (filepath, site_id, record_datetime)
 * - Search functionality through CommonTableSearchBar
 * - Click-to-open records in new tab
 * 
 * @fileoverview Main records listing page with filtering and pagination
 */

import type { Record } from "#gql/default";

// Set page layout to full-width for better table display
definePageMeta({ layout: "full-width" });

/**
 * Initialize records pagination composable
 * Provides reactive state for table data, pagination, sorting, and search
 */
const {
  page,                 // Current page number
  itemsPerPage,        // Items displayed per page
  sortBy,              // Current sort configuration
  items,               // Current page items
  totalItems,          // Total number of records
  isLoading: loading,  // Loading state
  handleReset,         // Reset search filters
  handleSearch         // Apply search filters
} = useRecordsPaginated();

// Set default sorting by filepath in ascending order
sortBy.value = [{ key: 'filepath', order: 'asc' }];

// Get runtime configuration (may be used for API endpoints)
const config = useRuntimeConfig();

/**
 * Pagination options for the data table footer
 * Allows users to choose how many records to display per page
 */
const paginationOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
  { value: 100, title: '100' },
];

/**
 * Table column definitions
 * Defines which fields to display, their alignment, sorting, and search capabilities
 * 
 * Key properties:
 * - title: Column header text
 * - key: Field path in the data object (supports nested paths like "site.name")
 * - align: Text alignment ("start", "center", "end")
 * - sortable: Whether column can be sorted
 * - search: Search configuration (false = no search, object = search settings)
 */
const headers = [
  // Site ID - searchable and sortable
  { 
    title: "Site Id", 
    key: "site_id", 
    align: "start", 
    sortable: true, 
    search: false
  },
  // Site prefix and site name combined
  { 
    title: "Site", 
    key: "site.prefix", 
    align: "start", 
    sortable: true, 
    search: false 
  },
  // Record timestamp - when the recording was made
  { 
    title: "Date & Time", 
    key: "record_datetime", 
    align: "start", 
    search: false 
  },
  // File path - main sortable field for file location
  { 
    title: "File Path", 
    key: "filepath", 
    align: "start", 
    sortable: true, 
    search: false
  },
  
  // Commented out fields that could be enabled in the future:
  // { title: "Record Id", key: "id", align: "end", search: false },
  // { title: "Record Type", key: "record_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Record Status", key: "record_status", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "File Size", key: "file_size", align: "end", search: { operator: "_eq", type: "number" } },
  // { title: "File Type", key: "file_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Duration", key: "duration", align: "end", search: { operator: "_eq", type: "number" } },
  // { title: "Channels", key: "channels", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Mime Type", key: "mime_type", align: "end", search: { operator: "_like", type: "text" } },
  // { title: "Sample Rate", key: "sample_rate", align: "end", search: { operator: "_eq", type: "number" } },
] as const;

/**
 * Handle click on table row to open record details
 * Opens the record detail page in a new browser tab
 * 
 * @param {string|number} id - The record ID to open
 */
function goToItem(id) {
  window.open(`records/${id}`, '_blank')
}

/**
 * Utility function to access nested object properties
 * Handles dot-notation paths like "site.name" to get nested values
 * 
 * @param {object} obj - The object to traverse
 * @param {string} key - Dot-notation path to the desired property
 * @returns {any} The value at the specified path, or undefined if not found
 * 
 * @example
 * getNested({site: {name: "Test Site"}}, "site.name") // Returns "Test Site"
 */
function getNested(obj, key) {
  return key.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
}

// Reactive reference for the currently selected site ID
const selectedSite = ref<number | null>(null);

/**
 * Site Filter Integration
 * Uses the useSiteFilter composable to get available sites for the dropdown
 * This provides a consistent way to access site data across the application
 */
const sitesFilter = useSiteFilter({});

/**
 * Computed property to transform site data for v-select component
 * Converts raw site objects into the format expected by Vuetify's v-select
 * 
 * Format: {title: "display text", value: "option value"}
 * Display shows: "site_prefix, site_name" (e.g., "ABC, Test Site")
 */
const sites = computed(() => {
  // Return empty array if no data available
  if (!sitesFilter.data.value) return [];
  
  // Transform each site into dropdown option format
  return sitesFilter.data.value.map(site => ({
    title: `${site.prefix}, ${site.name}`,  // Display format: "PREFIX, Name"
    value: site.id                          // Value used for filtering
  }));
});

/**
 * Watch for site selection changes and apply filter
 * When user selects a site from the dropdown, automatically filter records
 * When selection is cleared, remove the site filter
 * 
 * Uses GraphQL-style filter syntax: {site_id: {_eq: siteId}}
 */
watch(selectedSite, (newSiteId) => {
  if (newSiteId) {
    // Apply site filter when site is selected
    console.log('Site selected:', newSiteId);
    handleSearch({
      site_id: { _eq: newSiteId }
    });
  } else {
    // Clear site filter when selection is cleared
    handleSearch({
      site_id: { _eq: undefined }
    });
  }
});
</script>

<style scoped>
/**
 * Component Styles
 * 
 * These styles enhance the user experience by providing visual feedback
 * and ensuring consistent spacing and typography
 */

/* Hover effect for table rows - provides visual feedback that rows are clickable */
tr:hover {
  background-color: #f0f8ff;  /* Light blue background */
  cursor: pointer;            /* Pointer cursor indicates clickability */
}

/* Style for sortable column headers - makes them visually distinct */
.v-data-table-header__sortable {
  background-color: #f0f0f0;  /* Light grey background */
  font-weight: 800!important; /* Bold text for emphasis */
  cursor: pointer;            /* Pointer cursor for interaction */
}

/* Style for sort icons in column headers */
.v-data-table-header__sort-icon {
  color: #333;  /* Dark grey for good contrast */
}

/**
 * Fix for Vuetify data table footer dropdown
 * Prevents text truncation in the "Items per page" dropdown
 * Uses :deep() to penetrate component encapsulation
 */
:deep(.v-data-table-footer__items-per-page .v-select) {
  min-width: 100px;
}
</style>

<template>
  <!-- 
    Records Table Template
    
    Main container with fluid layout for full-width display
    Uses Vuetify's v-data-table-server for server-side operations
  -->
  <v-container fluid>
    <!-- Commented audio element - could be used for record preview -->
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
      
      <!-- 
        Top Section: Filters and Pagination
        Custom top slot containing filtering controls and pagination
        Uses responsive layout with filters on left, pagination on right
      -->
      <template v-slot:top>
        <v-row align="center" class="pa-2" no-gutters>
          <!-- Filter Controls Card -->
          <v-col cols="auto">
            <v-card class="pa-3 mr-4" variant="outlined" color="primary">
              <v-card-title class="text-subtitle-2 pa-0 mb-2">Quick Filters</v-card-title>
              
              <v-row no-gutters>
                <!-- Site Selection Dropdown -->
                <v-col cols="auto" class="mr-3">
                  <v-select
                    v-model="selectedSite"
                    label="Select site"
                    :items="sites"
                    density="compact"
                    variant="outlined"
                    clearable
                    style="min-width: 200px;"
                    prepend-inner-icon="mdi-access-point-network"
                  />
                </v-col>
                
                <!-- Date Display Field (currently disabled/read-only) -->
                <v-col cols="auto">
                  <v-text-field
                    label="Date"
                    density="compact"
                    variant="outlined"
                    disabled
                    style="min-width: 200px;"
                    prepend-inner-icon="mdi-calendar"
                  />
                </v-col>                
              </v-row>
            </v-card>
          </v-col>
          
          <!-- Spacer to push pagination to the right -->
          <v-spacer />
          
          <!-- 
           Pagination Controls (bottom) 
           The bottom pagination is automatically rendered by v-data-table-server
          -->
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

      <!-- 
        Table Header 
      -->
      <template v-slot:thead>
        <CommonTableSearchBar 
          :headers="headers" 
          @update:key="handleSearch" 
          @update:reset="handleReset" 
        />
      </template>
      
      <!-- 
        Table Row Template
        Custom template for each data row with click handler
      -->
      <template #item="{ item }">
        <tr @click="goToItem(item.id)" style="cursor: pointer;">
          <td v-for="header in headers" :key="header.key">
            <template v-if="header.key === 'site.prefix'">
              <!-- Display site prefix and name for site-related fields -->
              {{ item.site?.prefix }}, {{ item.site?.name }}
            </template>
            <template v-else>
              {{ getNested(item, header.key) }}
            </template>
          </td>
        </tr>
      </template>
      
    </v-data-table-server>
  </v-container>
</template>