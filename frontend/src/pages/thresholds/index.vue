<script setup lang="ts">
import type { ThresholdItem } from "~/composables/api/thresholds";
import { useThresholdsPaginated } from "~/composables/api/thresholds";

// Set page layout to full-width for better table display
definePageMeta({ layout: "full-width" });

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
 * Initialize threshold pagination composable
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
} = useThresholdsPaginated();

// Set default sorting by id in descending order
sortBy.value = [{ key: 'id', order: 'desc' }];

// Get runtime configuration (may be used for API endpoints)
const config = useRuntimeConfig();

/**
 * Utility function to access nested object properties
 * Handles dot-notation paths like "label.name" to get nested values
 *
 * @param {object} obj - The object to traverse
 * @param {string} key - Dot-notation path to the desired property
 * @returns {any} The value at the specified path, or undefined if not found
 *
 * @example
 * getNested({label: {name: "Test Label"}}, "label.name") // Returns "Test Label"
 */
function getNested(obj: any, key: string) {
  return key.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
}

const headers = [
  {
    title: "ID",
    key: "id",
    align: "end",
    sortable: true,
    search: false
  },
  {
    title: "Label",
    key: "label.name",
    align: "start",
    sortable: true,
    search: { operator: "_like", type: "text" }
  },
  {
    title: "Model",
    key: "model.name",
    align: "start",
    sortable: true,
    search: { operator: "_like", type: "text" }
  },
  {
    title: "Threshold",
    key: "threshold",
    align: "end",
    sortable: true,
    search: { operator: "_eq", type: "number" }
  },
  {
    title: "Is Final",
    key: "is_final",
    align: "center",
    sortable: true,
    search: { operator: "_eq", type: "boolean" }
  },
  {
    title: "Set At",
    key: "set_at",
    align: "start",
    sortable: true,
    search: false
  },
] as const;
</script>

<template>
  <v-container fluid>
    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="items"
      :items-length="totalItems"
      :loading="loading"
      item-value="id"
      :items-per-page-options="paginationOptions"
      >
      <!--
        Table Row Template
        Custom template for each data row with proper nested data handling
      -->
      <template #item="{ item }">
        <tr>
          <td v-for="header in headers" :key="header.key">
            {{ getNested(item, header.key) }}
          </td>
        </tr>
      </template>
    </v-data-table-server>
  </v-container>

</template>