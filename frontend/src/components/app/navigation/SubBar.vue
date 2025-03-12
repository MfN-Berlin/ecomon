<script setup lang="ts">
type Item = {
  id: number;
  name: string;
  [key: string]: unknown; // Add any other properties here
};
type Props = {
  loading: boolean;
  data: Item[];
  rootPath: string;
};
type Emits = {
  (e: "fetch-next-page"): void;
  (e: "search", term: string): void;
};
const emits = defineEmits<Emits>();
defineProps<Props>();
const { model: search, value: searchTerm } = useSearchTrigger((value: string) => emits("search", value), {
  debounce: 400
});

onMounted(() => {
  emits("search", searchTerm.value);
});
// Optional: Watch for changes in the surrounding layout and update the height
</script>
<template>
  <v-container class="pa-0 h-100 d-flex flex-nowrap flex-column">
    <v-toolbar flat density="compact" class="px-2" color="surface">
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

      <NuxtLink :to="`${rootPath}/create`">
        <v-btn icon density="compact" color="primary" variant="tonal"><v-icon>mdi-plus</v-icon> </v-btn>
      </NuxtLink>
    </v-toolbar>
    <div class="flex-grow-1 overflow-auto">
      <common-infinite-scroller :loading="loading" @load-more="emits('fetch-next-page')">
        <template #content>
          <v-list color="primary" density="compact" nav>
            <v-list-item
              v-for="item in data"
              :key="item.id"
              :to="`${rootPath}/${item.id}`"
              link
              :title="item.name"
            ></v-list-item>
          </v-list>
        </template>
        <template #loading>
          <v-sheet class="py-2 d-flex justify-center align-center">
            <v-progress-circular color="secondary" indeterminate></v-progress-circular>
          </v-sheet>
        </template>
      </common-infinite-scroller>
    </div>
  </v-container>
</template>
