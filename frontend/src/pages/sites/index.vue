<!--
Site index page component.  

  Description:
    This Vue component/page is responsible for rendering and managing the user interface for [describe its purpose]. 
    It handles state management, event handling, and any data-fetching or processing required to display the content correctly.

  Key Functionalities:
    • Initialization: Sets up the component state and performs any necessary data fetching when the component is mounted.
    • Data Binding: Uses Vue's reactivity system to automatically update the DOM when data changes.
    • Event Handling: Listens for user interactions (e.g., clicks, form submissions) and triggers appropriate handler methods.
    • Computed Properties & Watchers: Manages derived state and reacts to changes in dependent data properties.
    • Integration: May interact with external APIs or services to retrieve or update data as needed.

  Usage and Integration:
    • Import and use this component within your Vue application's routing configuration or as a nested component.
    • Ensure any required props or dependencies are provided by the parent component or during component registration.
    • Customize the component by modifying its state, methods, and styles to match the desired behavior and appearance.

  Additional Notes:
    • Be sure to document any custom methods and lifecycle hooks inside their respective sections for clearer maintainability.
    • Review and update the inline comments as the component evolves to keep the documentation accurate.

    @see: components/app/navigation/SubBar.vue for a reusable navigation sub-bar component.
-->
<script setup lang="ts">
import type { GetSitesPaginatedQuery } from "#gql";

// Type definition for individual site items from GraphQL query
// the query itself is in: ecomon/frontend/src/queries/sites.gql
type Site = GetSitesPaginatedQuery["items"][number];

// Use submenu layout for consistent navigation with other sections
definePageMeta({ layout: "submenu" });

// Pagination and data management composable
const {
  page,           // Current page number
  itemsPerPage,   // Number of items to display per page
  sortBy,         // Current sorting configuration
  items,          // Array of site items for current page
  totalItems,     // Total number of sites (for pagination)
  isLoading: loading,  // Loading state for data fetching
  handleReset,    // Function to reset all filters and search
  handleSearch    // Function to handle search queries
} = useSitePaginated();

// Table column configuration with search capabilities
const headers = [
  { title: "ID", key: "id", align: "end", search: { operator: "_eq", type: "number" } },
  { title: "name", key: "name", align: "end", search: { operator: "_like", type: "text" } },
  { title: "prefix", key: "prefix", align: "end", search: { operator: "_like", type: "text" } },
  {
    title: "record_regime_pause_duration",
    key: "record_regime_pause_duration",
    align: "end",
    search: false // No search functionality for this field
  },
  {
    title: "record_regime_recording_duration",
    key: "record_regime_recording_duration",
    align: "end",
    search: false // No search functionality for this field
  },
  { title: "sample_rate", key: "sample_rate", align: "end", search: { operator: "_eq", type: "number" } }
] as const;

// Computed property to generate map markers from sites with valid coordinates
const markers = computed(() => {
  return (items.value as Site[])
    .filter((item) => item.location.lat && item.location.long)
    .map((item) => ({
      id: item.id,
      name: item.name,
      lat: item.location.lat,
      long: item.location.long,
      to: `/sites/${item.id}`  // Navigation link to site details
    }));
});
</script>

<template>
  <v-container>
    <!-- Interactive map showing site locations -->
    <BaseMap :markers="markers" />

    <!-- Server-side data table with pagination and sorting -->
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
      <!-- Custom table header with search functionality -->
      <template v-slot:thead>
        <CommonTableSearchBar 
          :headers="headers" 
          @update:key="handleSearch"    
          @update:reset="handleReset"   
        />
      </template>
    </v-data-table-server>
  </v-container>
</template>
