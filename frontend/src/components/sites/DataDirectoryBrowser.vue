<script setup lang="ts">
const emit = defineEmits<{
  (e: "select", path: string[]): void;
  (e: "cancel"): void;
}>();
const params = ref({ subpath: "" });
const { data, isPending } = useSiteListDataDirectories(params);
const breadcrumbs = computed(() => ["data", ...params.value.subpath.split("/").filter(Boolean)]);

// Add computed property to determine if we're at root
const isRoot = computed(() => !params.value.subpath);
const directorySelection = ref<number[]>([]);
function handleClick(path: string) {
  params.value.subpath = path;
  directorySelection.value = [];
}

// Add function to go up one level
function goUp() {
  const parts = params.value.subpath.split("/").filter(Boolean);
  parts.pop();
  params.value.subpath = parts.join("/");
  directorySelection.value = [];
}

// Add function to handle breadcrumb clicks
function handleBreadcrumbClick(index: number) {
  if (index === 0) {
    // Clicking "Data" returns to root
    params.value.subpath = "";
  } else {
    // Get path up to clicked breadcrumb
    const parts = params.value.subpath.split("/").filter(Boolean);
    params.value.subpath = parts.slice(0, index).join("/");
    directorySelection.value = [];
  }
}

function handleSelect() {
  emit("select", [params.value.subpath]);
}

function handleMultiSelect() {
  if (!data || !data.value) return;
  emit(
    "select",
    directorySelection.value.map((dirIndex) => data.value![dirIndex]!.path)
  );
}
</script>

<template>
  <v-card height="400">
    <v-card-title class="d-flex justify-space-between"> Select Directory </v-card-title>
    <v-card-text class="pa-0">
      <div class="d-flex justify-space-between">
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
        <v-btn-group variant="text" divided>
          <v-btn
            v-if="directorySelection.length > 0"
            class="mr-2"
            icon="mdi-playlist-remove"
            @click="directorySelection = []"
          ></v-btn>
        </v-btn-group>
      </div>
      <v-item-group v-model="directorySelection" multiple>
        <v-list class="directory-list" height="250" style="overflow-y: auto">
          <!-- Back button when not at root -->
          <v-skeleton-loader v-if="isPending" type="list-item-three-line"></v-skeleton-loader>
          <v-list-item
            v-if="!isRoot && !isPending"
            :style="{ cursor: 'pointer' }"
            density="compact"
            @click="goUp"
          >
            <template #prepend>
              <v-icon>mdi-arrow-up</v-icon>
            </template>
            <v-list-item-title>..</v-list-item-title>
          </v-list-item>

          <v-list-item v-for="item in data" :key="item.path" :style="{ cursor: 'pointer' }" density="compact">
            <template #prepend>
              <v-icon>mdi-folder</v-icon>
            </template>
            <template #append>
              <v-item v-slot="{ isSelected, toggle }">
                <v-checkbox-btn :value="isSelected" density="compact" @click="toggle"></v-checkbox-btn>
              </v-item>
            </template>
            <v-list-item-title @click="handleClick(item.path)">{{ item.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-item-group>
    </v-card-text>
    <v-card-actions>
      <v-btn @click="emit('cancel')">Cancel</v-btn>
      <v-spacer></v-spacer>
      <v-btn v-if="directorySelection.length == 0" color="primary" @click="handleSelect">
        Select This Directory
      </v-btn>
      <v-btn v-else color="primary" @click="handleMultiSelect">
        Select These {{ directorySelection.length }} Directories
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.directory-list {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
