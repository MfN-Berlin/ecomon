<script setup lang="ts">
const emit = defineEmits<{
  (e: "select", path: string[]): void;
  (e: "cancel"): void;
}>();
const props = defineProps<{
  directories: string[];
}>();

const params = ref({ subpath: "" });
const { data, isPending } = useSiteListDataDirectories(params);

const isRoot = computed(() => !params.value.subpath);
const breadcrumbs = computed(() => ["data", ...params.value.subpath.split("/").filter(Boolean)]);
const directorySelection = ref<number[]>([]);
const restrictedLetters = ["U", "V", "W", "X", "Y", "Z"];

const sortedData = computed(() => {
  if (!data?.value) return [];
  return [...(data.value ?? [])].sort((a, b) => a.name.localeCompare(b.name));
});

const endsWithRestrictedLetter = (name: string) => {
  const lastChar = name.slice(-1).toUpperCase();
  return restrictedLetters.includes(lastChar);
};

const isDisabled = (item: any) => {
  return props.directories.includes(item?.path) || endsWithRestrictedLetter(item.name);
};

function handleClick(path: string) {
  params.value.subpath = path;
  directorySelection.value = [];
}

function goUp() {
  const parts = params.value.subpath.split("/").filter(Boolean);
  parts.pop();
  params.value.subpath = parts.join("/");
  directorySelection.value = [];
}

function handleBreadcrumbClick(index: number) {
  params.value.subpath = index === 0 ? "" : params.value.subpath.split("/").filter(Boolean).slice(0, index).join("/");
  directorySelection.value = [];
}

function handleSelect() {
  emit("select", [params.value.subpath]);
}

function handleMultiSelect() {
  if (!data?.value) return;
  emit("select", directorySelection.value.map((dirIndex) => data.value![dirIndex]!.path));
}
</script>

<template>
  <v-card height="400">
    <v-toolbar title="Select Directory" color="primary" />
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
          <v-btn v-if="directorySelection.length" class="mr-2" icon="mdi-playlist-remove" @click="directorySelection = []" />
        </v-btn-group>
      </div>
      <v-item-group v-model="directorySelection" multiple>
        <v-list class="directory-list" height="250" style="overflow-y: auto">
          <v-skeleton-loader v-if="isPending" type="list-item-three-line" />
          <v-list-item v-if="!isRoot && !isPending" style="cursor: pointer" density="compact" @click="goUp">
            <template #prepend>
              <v-icon>mdi-arrow-up</v-icon>
            </template>
            <v-list-item-title>..</v-list-item-title>
          </v-list-item>

          <v-list-item
            v-for="item in sortedData"
            :key="item.path"
            :style="{ cursor: endsWithRestrictedLetter(item.name) ? 'not-allowed' : 'pointer' }"
            density="compact"
            :disabled="isDisabled(item)"
          >
            <template #prepend>
              <v-icon>mdi-folder</v-icon>
            </template>
            <v-list-item-title
              :class="{ 'text-disabled': endsWithRestrictedLetter(item.name) }"
              @click="!endsWithRestrictedLetter(item.name) ? handleClick(item.path) : null"
            >
              {{ item.name }}
            </v-list-item-title>
            <template #append>
              <v-item v-slot="{ isSelected, toggle }">
                <v-checkbox :model-value="isSelected" density="compact" @click="toggle" />
              </v-item>
            </template>
          </v-list-item>
        </v-list>
      </v-item-group>
    </v-card-text>
    <v-card-actions>
      <v-btn @click="emit('cancel')">Cancel</v-btn>
      <v-spacer />
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