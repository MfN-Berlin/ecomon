<script setup lang="ts">
/**
 * Component events for directory selection and cancellation
 */
const emit = defineEmits<{
  (e: "select", path: string[]): void;
  (e: "cancel"): void;
}>();

/**
 * Component props
 */
const props = defineProps<{
  directories: string[]; // Already selected directories to prevent duplicates
}>();

// Current navigation state
const params = ref({ subpath: "" });
const { data, isPending } = useSiteListDataDirectories(params);

// Log the root directory path when component mounts
onMounted(() => {
  console.log('DataDirectoryBrowser mounted');
  console.log('Initial params:', params.value);
  console.log('Initial subpath:', params.value.subpath);
  console.log('Is at root:', isRoot.value);
});
// Watch for changes in data to log root directory information
watch(data, (newData) => {
  if (newData && newData.length > 0) {
    console.log('Root directory data loaded:', newData);
    console.log('Number of directories in root:', newData.length);
    console.log('Root directory names:', newData.map(item => item.name));
    console.log('Root directory paths:', newData.map(item => item.path));
  }
}, { immediate: true });

// Watch for navigation changes
watch(() => params.value.subpath, (newSubpath, oldSubpath) => {
  console.log('Navigation changed:');
  console.log('  From:', oldSubpath || '(root)');
  console.log('  To:', newSubpath || '(root)');
  console.log('  Current breadcrumbs:', breadcrumbs.value);
});


// Computed properties for UI state
const isRoot = computed(() => !params.value.subpath);
const breadcrumbs = computed(() => ["data", ...params.value.subpath.split("/").filter(Boolean)]);
const directorySelection = ref<number[]>([]);

// Name of directories with bat recordings end with U (ultrasonic) and following letters
// Directories ending with these letters are restricted from selection
const restrictedLetters = ["U", "V", "W", "X", "Y", "Z"];

/**
 * Sorts directories alphabetically by name
 */
const sortedData = computed(() => {
  if (!data?.value) return [];
  return [...(data.value ?? [])].sort((a, b) => a.name.localeCompare(b.name));
});

/**
 * Checks if directory name ends with restricted letter
 */
const endsWithRestrictedLetter = (name: string) => {
  const lastChar = name.slice(-1).toUpperCase();
  return restrictedLetters.includes(lastChar);
};

/**
 * Determines if directory item should be disabled
 */
const isDisabled = (item: any) => {
  console.log('props.directories:', props.directories);
  console.log('Checking if item is disabled:', item.path, props.directories.includes(item?.path));
  return props.directories.includes(item?.path) || endsWithRestrictedLetter(item.name);
};

/**
 * Navigates into selected directory
 */
function handleClick(path: string) {
  params.value.subpath = path;
  directorySelection.value = [];
}

/**
 * Navigates up one level in directory tree
 */
function goUp() {
  const parts = params.value.subpath.split("/").filter(Boolean);
  parts.pop();
  params.value.subpath = parts.join("/");
  directorySelection.value = [];
}

/**
 * Handles breadcrumb navigation
 */
function handleBreadcrumbClick(index: number) {
  params.value.subpath = index === 0 ? "" : params.value.subpath.split("/").filter(Boolean).slice(0, index).join("/");
  directorySelection.value = [];
}

/**
 * Emits selection of current directory (fixed to handle checkbox selections)
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
 * Emits selection of multiple directories (fixed indexing)
 */
function handleMultiSelect() {
  if (!data?.value) return;
  
  console.log('Directory selection indices:', directorySelection.value);
  console.log('Sorted data:', sortedData.value);
  console.log('Original data:', data.value);
  
  const selectedPaths = directorySelection.value.map((dirIndex) => {
    // Make sure we're using the sorted data, not the original data
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
  <!-- Main card container for directory browser -->
  <v-card height="400">
    <!-- Header toolbar -->
    <v-toolbar title="Select Directory" color="primary" />
    
    <v-card-text class="pa-0">
      <!-- Navigation breadcrumbs and clear selection button -->
      <div class="d-flex justify-space-between">
        <!-- Breadcrumb navigation -->
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
      
      <!-- Directory selection group for multiple selections -->
      <v-item-group v-model="directorySelection" multiple>
        <!-- Scrollable directory list -->
        <v-list class="directory-list" height="250" style="overflow-y: auto">
          <!-- Loading skeleton while data is pending -->
          <v-skeleton-loader v-if="isPending" type="list-item-three-line" />
          
          <!-- "Go up" button (only shown when not at root) -->
          <v-list-item v-if="!isRoot && !isPending" style="cursor: pointer" density="compact" @click="goUp">
            <template #prepend>
              <v-icon>mdi-arrow-up</v-icon>
            </template>
            <v-list-item-title>..</v-list-item-title>
          </v-list-item>

          <!-- Directory items -->
          <v-list-item
            v-for="item in sortedData"
            :key="item.path"
            :style="{ cursor: endsWithRestrictedLetter(item.name) ? 'not-allowed' : 'pointer' }"
            density="compact"
            :disabled="isDisabled(item)"
          >
            <!-- Folder icon -->
            <template #prepend>
              <v-icon>mdi-folder</v-icon>
            </template>
            
            <!-- Directory name (clickable if not restricted) -->
            <v-list-item-title
              :class="{ 'text-disabled': endsWithRestrictedLetter(item.name) }"
              @click="!endsWithRestrictedLetter(item.name) ? handleClick(item.path) : null"
            >
              {{ item.name }}
            </v-list-item-title>
            
            <!-- Selection checkbox -->
            <template #append>
              <v-item v-slot="{ isSelected, toggle }">
                <v-checkbox :model-value="isSelected" density="compact" @click="toggle" />
              </v-item>
            </template>
          </v-list-item>
        </v-list>
      </v-item-group>
    </v-card-text>
    
    <!-- Action buttons -->
    <v-card-actions>
      <!-- Cancel button -->
      <v-btn @click="emit('cancel')">Cancel</v-btn>
      <v-spacer />
      
      <!-- Dynamic select button -->
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
.directory-list {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
.text-disabled {
  color: rgba(0, 0, 0, 0.38);
  cursor: not-allowed;
}
</style>