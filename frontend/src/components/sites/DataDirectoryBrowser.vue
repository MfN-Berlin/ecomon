<script setup lang="ts">
const emit = defineEmits<{
  (e: "select", path: string): void;
}>();
const params = ref({ subpath: "" });
const { data } = useSiteListDataDirectories(params);
const breadcrumbs = computed(() => ["Data", ...params.value.subpath.split("/").filter(Boolean)]);

// Add computed property to determine if we're at root
const isRoot = computed(() => !params.value.subpath);

function handleClick(path: string) {
  params.value.subpath = path;
}

// Add function to go up one level
function goUp() {
  const parts = params.value.subpath.split("/").filter(Boolean);
  parts.pop();
  params.value.subpath = parts.join("/");
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
  }
}

function handleSelect() {
  emit("select", params.value.subpath);
}
</script>

<template>
  <v-card height="400">
    <v-card-title>Select Directory</v-card-title>
    <v-card-text class="pa-0">
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

      <v-list class="directory-list" height="250" style="overflow-y: auto">
        <!-- Back button when not at root -->
        <v-list-item v-if="!isRoot" :style="{ cursor: 'pointer' }" density="compact" @click="goUp">
          <template #prepend>
            <v-icon>mdi-arrow-up</v-icon>
          </template>
          <v-list-item-title>..</v-list-item-title>
        </v-list-item>

        <v-list-item
          v-for="item in data"
          :key="item.path"
          :style="{ cursor: 'pointer' }"
          density="compact"
          @click="handleClick(item.path)"
        >
          <template #prepend>
            <v-icon>mdi-folder</v-icon>
          </template>
          <v-list-item-title>{{ item.name }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="handleSelect"> Select This Directory </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.directory-list {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
