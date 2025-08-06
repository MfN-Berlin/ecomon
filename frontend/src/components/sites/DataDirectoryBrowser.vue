<script setup lang="ts">
/**
 * DataDirectoryBrowser Component
 * 
 * A file browser component for navigating and selecting directories from site data.
 * Features:
 * - Directory navigation with breadcrumb trail
 * - Single and multiple directory selection via checkboxes
 * - Disabled state for restricted directories (ending with U-Z) and already selected directories
 * - Alphabetical sorting of directories
 * - Real-time filtering to prevent duplicate selections
 * 
 * @component
 * @example
 * <DataDirectoryBrowser
 *   :directories="existingDirectories"
 *   @select="onDirectorySelected"
 *   @cancel="onCancel"
 * />
 */

/**
 * Component events for directory selection and cancellation
 */
const emit = defineEmits<{
  /** Emitted when directories are selected - returns array of full directory paths */
  (e: "select", path: string[]): void;
  /** Emitted when user cancels the selection dialog */
  (e: "cancel"): void;
}>();

/**
 * Component props
 */
const props = defineProps<{
  /** Array of already selected directory paths to prevent duplicates from being selectable */
  directories: string[]; // Already selected directories to prevent duplicates
}>();

/**
 * Current navigation state - tracks the current subdirectory path being browsed
 */
const params = ref({ subpath: "" });

/**
 * Reactive data fetching for directory contents based on current navigation path
 */
const { data, isPending } = useSiteListDataDirectories(params);

/**
 * Component lifecycle - Log initial state for debugging
 */
onMounted(() => {
  console.log('DataDirectoryBrowser mounted');
  console.log('Initial params:', params.value);
  console.log('Initial subpath:', params.value.subpath);
  console.log('Is at root:', isRoot.value);
});

/**
 * Watch for data changes to log directory information for debugging
 */
watch(data, (newData) => {
  if (newData && newData.length > 0) {
    console.log('Root directory data loaded:', newData);
    console.log('Number of directories in root:', newData.length);
    console.log('Root directory names:', newData.map(item => item.name));
    console.log('Root directory paths:', newData.map(item => item.path));
  }
}, { immediate: true });

/**
 * Watch for navigation changes to log path transitions for debugging
 */
watch(() => params.value.subpath, (newSubpath, oldSubpath) => {
  console.log('Navigation changed:');
  console.log('  From:', oldSubpath || '(root)');
  console.log('  To:', newSubpath || '(root)');
  console.log('  Current breadcrumbs:', breadcrumbs.value);
});

/**
 * Computed property to determine if user is at the root directory level
 */
const isRoot = computed(() => !params.value.subpath);

/**
 * Computed property for breadcrumb navigation trail
 * Creates array starting with "data" followed by each directory level
 */
const breadcrumbs = computed(() => ["data", ...params.value.subpath.split("/").filter(Boolean)]);

/**
 * Reactive array storing the indices of selected directories for checkbox selection
 */
const directorySelection = ref<number[]>([]);

/**
 * Letters that indicate ultrasonic bat recording directories
 * Directories ending with these letters are restricted from selection
 * Name of directories with bat recordings end with U (ultrasonic) and following letters
 */
const restrictedLetters = ["U", "V", "W", "X", "Y", "Z"];

/**
 * Computed property that sorts directories alphabetically by name
 * Ensures consistent display order regardless of API response order
 * @returns Sorted array of directory objects
 */
const sortedData = computed(() => {
  if (!data?.value) return [];
  return [...(data.value ?? [])].sort((a, b) => a.name.localeCompare(b.name));
});

/**
 * Checks if a directory name ends with a restricted letter (U-Z)
 * These directories contain ultrasonic recordings and should not be selectable
 * @param name - Directory name to check
 * @returns True if directory ends with restricted letter
 */
const endsWithRestrictedLetter = (name: string) => {
  const lastChar = name.slice(-1).toUpperCase();
  return restrictedLetters.includes(lastChar);
};

/**
 * Determines if a directory item should be disabled for selection
 * Disabled if:
 * - Already exists in props.directories (prevents duplicates)
 * - Ends with restricted letter (ultrasonic recordings)
 * @param item - Directory item to check
 * @returns True if directory should be disabled
 */
const isDisabled = (item: any) => {
  console.log('props.directories:', props.directories);
  console.log('Checking if item is disabled:', item.path, props.directories.includes(item?.path));
  return props.directories.includes(item?.path) || endsWithRestrictedLetter(item.name);
};

/**
 * Navigates into the selected directory
 * Updates the subpath to show contents of clicked directory and clears any checkbox selections
 * @param path - Full path of directory to navigate into
 */
function handleClick(path: string) {
  params.value.subpath = path;
  directorySelection.value = [];
}

/**
 * Navigates up one level in the directory tree
 * Removes the last directory from the current path and clears selections
 */
function goUp() {
  const parts = params.value.subpath.split("/").filter(Boolean);
  parts.pop();
  params.value.subpath = parts.join("/");
  directorySelection.value = [];
}

/**
 * Handles breadcrumb navigation to jump to specific directory level
 * Allows quick navigation to any parent directory in the current path
 * @param index - Index in breadcrumb array (0 = root, 1+ = directory levels)
 */
function handleBreadcrumbClick(index: number) {
  params.value.subpath = index === 0 ? "" : params.value.subpath.split("/").filter(Boolean).slice(0, index).join("/");
  directorySelection.value = [];
}

/**
 * Handles directory selection - either checkbox selections or current directory
 * If checkboxes are selected, delegates to handleMultiSelect()
 * Otherwise, selects the current navigated directory
 * This is the main selection handler called by the UI button
 */
function handleSelect() {
  // If there are checkbox selections, use those instead of current path
  if (directorySelection.value.length > 0) {
    handleMultiSelect();
    return;
  }
  
  // Otherwise, select the current navigated directory
  const currentPath = params.value.subpath || '';
  console.log('Selecting current directory:', currentPath);
  emit("select", [currentPath]);
}

/**
 * Handles multiple directory selection from checkboxes
 * Maps selected indices to full directory paths and emits the selection
 * 
 * IMPORTANT: Uses sortedData instead of original data to ensure indices match
 * the displayed order in the UI (fixes indexing bug where wrong directories were selected)
 */
function handleMultiSelect() {
  if (!data?.value) return;
  
  console.log('Directory selection indices:', directorySelection.value);
  console.log('Sorted data:', sortedData.value);
  console.log('Original data:', data.value);
  
  const selectedPaths = directorySelection.value.map((dirIndex) => {
    // Make sure we're using the sorted data, not the original data
    // This ensures the index matches what's displayed in the UI
    const selectedDir = sortedData.value[dirIndex];
    
    console.log(`Index ${dirIndex} maps to:`, selectedDir);
    
    if (!selectedDir) {
      console.error(`No directory found at index ${dirIndex}`);
      return null;
    }
    
    // Build the full path by combining current subpath with selected directory name
    const fullPath = params.value.subpath 
      ? `${params.value.subpath}/${selectedDir.name}`
      : selectedDir.name;
    
    console.log('Selected directory full path:', fullPath);
    return fullPath;
  }).filter(Boolean); // Remove any null values
  
  console.log('Multi-selecting directories:', selectedPaths);
  emit("select", selectedPaths);
}
</script>

<template>
  <!-- Main card container for directory browser with fixed height -->
  <v-card height="400">
    <!-- Header toolbar with title and primary color -->
    <v-toolbar title="Select Directory" color="primary" />
    
    <v-card-text class="pa-0">
      <!-- Navigation breadcrumbs and clear selection button container -->
      <div class="d-flex justify-space-between">
        <!-- Breadcrumb navigation for quick directory jumping -->
        <v-breadcrumbs :items="breadcrumbs" class="px-4">
          <template #title="{ item, index }">
            <span
              :class="{ 'text-primary font-weight-medium': index === breadcrumbs.length - 1 }"
              style="opacity: 1; cursor: pointer"
              @click="handleBreadcrumbClick(index)"
            >
              {{ item.title }}
            </span>
          </template>
        </v-breadcrumbs>
        
        <!-- Clear selection button (only visible when items are selected) -->
        <v-btn-group variant="text" divided>
          <v-btn v-if="directorySelection.length" class="mr-2" icon="mdi-playlist-remove" @click="directorySelection = []" />
        </v-btn-group>
      </div>
      
      <!-- Directory selection group for multiple selections using v-item-group -->
      <v-item-group v-model="directorySelection" multiple>
        <!-- Scrollable directory list with fixed height -->
        <v-list class="directory-list" height="250" style="overflow-y: auto">
          <!-- Loading skeleton while data is pending from API -->
          <v-skeleton-loader v-if="isPending" type="list-item-three-line" />
          
          <!-- "Go up" button (only shown when not at root level) -->
          <v-list-item v-if="!isRoot && !isPending" style="cursor: pointer" density="compact" @click="goUp">
            <template #prepend>
              <v-icon>mdi-arrow-up</v-icon>
            </template>
            <v-list-item-title>..</v-list-item-title>
          </v-list-item>

          <!-- Directory items with navigation and selection capabilities -->
          <v-list-item
            v-for="item in sortedData"
            :key="item.path"
            :style="{ cursor: endsWithRestrictedLetter(item.name) ? 'not-allowed' : 'pointer' }"
            density="compact"
            :disabled="isDisabled(item)"
          >
            <!-- Folder icon for visual consistency -->
            <template #prepend>
              <v-icon>mdi-folder</v-icon>
            </template>
            
            <!-- Directory name (clickable for navigation if not restricted) -->
            <v-list-item-title
              :class="{ 'text-disabled': endsWithRestrictedLetter(item.name) }"
              @click="!endsWithRestrictedLetter(item.name) ? handleClick(item.path) : null"
            >
              {{ item.name }}
            </v-list-item-title>
            
            <!-- Selection checkbox for multi-select functionality -->
            <template #append>
              <v-item v-slot="{ isSelected, toggle }">
                <v-checkbox :model-value="isSelected" density="compact" @click="toggle" />
              </v-item>
            </template>
          </v-list-item>
        </v-list>
      </v-item-group>
    </v-card-text>
    
    <!-- Action buttons for cancel and select operations -->
    <v-card-actions>
      <!-- Cancel button to close dialog without selection -->
      <v-btn @click="emit('cancel')">Cancel</v-btn>
      <v-spacer />
      
      <!-- Dynamic select button that changes text based on selection count -->
      <v-btn
        color="primary"
        @click="directorySelection.length === 1 ? handleSelect() : handleMultiSelect()"
        :disabled="directorySelection.length === 0"
      >
        {{ 
          directorySelection.length === 0 ? "Select This Directory" : directorySelection.length === 1
          ? "Select This Directory" 
          : `Select These ${directorySelection.length} Directories` 
        }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
/**
 * Styling for the directory list with visual borders
 * Provides clear separation between navigation and content areas
 */
.directory-list {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

/**
 * Styling for disabled/restricted directory items
 * Makes restricted directories visually distinct and non-interactive
 */
.text-disabled {
  color: rgba(0, 0, 0, 0.38);
  cursor: not-allowed;
}
</style>