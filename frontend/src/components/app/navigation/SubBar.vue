<!--
  SubBar.vue
  Navigation component for displaying a list of items with search and infinite scroll functionality.
  Supports different root paths (e.g., '/sites', '/locations') with specific sorting and display logic.
-->
<script setup lang="ts">
/**
 * Represents an item in the navigation list
 */
type Item = {
  id: number;
  name: string;
  prefix?: string; // Optional prefix used for sites
  [key: string]: unknown;
};

/**
 * Component props definition
 */
type Props = {
  loading: boolean; // Loading state for infinite scroll
  data: Item[]; // Array of items to display
  rootPath: string; // Base path for navigation (e.g., '/sites', '/locations')
  name: string; // Display name for the section
};

/**
 * Component events definition
 */
type Emits = {
  (e: "fetch-next-page"): void; // Triggered when more data is needed
  (e: "search", term: string): void; // Triggered when search term changes
};

const emits = defineEmits<Emits>();
const props = defineProps<Props>();

/**
 * Search functionality with debounce
 */
const { model: search, value: searchTerm } = useSearchTrigger(
  (value: string) => emits("search", value), 
  { debounce: 400 }
);

/**
 * Determines the appropriate title based on the current page
 * Sites use prefix, other pages use name
 */
const getItemTitle = (item: Item) => {
  return props.rootPath === '/sites' ? item.prefix || item.name : item.name;
};

/**
 * Sorts data based on the current page type
 * Sites are sorted by prefix, others by name
 */
const sortedData = computed(() => {
  if (props.rootPath === '/sites') {
    // Sort sites by prefix (fallback to name)
    return [...props.data].sort((a, b) => {
      const aTitle = a.prefix || a.name || '';
      const bTitle = b.prefix || b.name || '';
      return aTitle.localeCompare(bTitle);
    });
  }
  // Sort other pages by name
  return [...props.data].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
});

/**
 * Initialize search on component mount
 */
onMounted(() => {
  emits("search", searchTerm.value);
});
</script>

<template>
  <!-- Main container with full height and flex layout -->
  <v-container class="pa-0 h-100 d-flex flex-nowrap flex-column">
    <!-- Top toolbar with search and create button -->
    <v-toolbar flat density="compact" class="px-2" color="surface">
      <!-- Search input field -->
      <v-text-field
        v-model="search"
        density="compact"
        color="primary"
        prepend-icon="mdi-magnify"
        hide-details
        single-line
        variant="underlined"
      ></v-text-field>
      <v-spacer></v-spacer>

      <!-- Create new item button -->
      <NuxtLink :to="`${rootPath}/create`">
        <v-tooltip :text="`Create new ${name}`" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn icon density="compact" color="primary" v-bind="props" variant="tonal">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
        </v-tooltip>
      </NuxtLink>
    </v-toolbar>

    <!-- Scrollable content area -->
    <div class="flex-grow-1 overflow-auto">
      <!-- Infinite scroll wrapper -->
      <common-infinite-scroller :loading="loading" @load-more="emits('fetch-next-page')">
        <template #content>
          <!-- Navigation list -->
          <v-list color="primary" density="compact" nav>

            <!-- Sites page: List item with tooltip showing full name -->
            <template v-if="rootPath === '/sites'">
            <v-tooltip 
              v-for="item in sortedData"
              :key="item.id"
              :text="item.name"
              location="right"
            >
              <template v-slot:activator="{ props: tooltipProps }">
                <v-list-item
                  :to="`${rootPath}/${item.id}`"
                  link
                  :title="getItemTitle(item)"
                  v-bind="tooltipProps"
                ></v-list-item>
              </template>
            </v-tooltip>
            </template>

            <!-- Other pages: List item without tooltip -->
            <template v-else>
              <v-list-item
                v-for="item in sortedData"
                :key="item.id"
                :to="`${rootPath}/${item.id}`"
                link
                :title="getItemTitle(item)"
              ></v-list-item>
            </template>
          </v-list>
        </template>
        
        <!-- Loading indicator -->
        <template #loading>
          <v-sheet class="py-2 d-flex justify-center align-center">
            <v-progress-circular color="secondary" indeterminate></v-progress-circular>
          </v-sheet>
        </template>
      </common-infinite-scroller>
    </div>
  </v-container>
</template>