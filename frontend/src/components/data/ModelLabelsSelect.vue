<script lang="ts" setup>
import { onMounted, watch, ref } from "vue";

import useModelLabelsList from "@/composables/api/useModelLabelsList";

const props = defineProps<{
  modelId?: number | null;
}>();

type DoneType = ((state: "ok" | "empty" | "error") => void) | null;
const selectedLabels = defineModel<[number] | null>();
const setInfiniteScrollState = ref<DoneType>(null);
watch(
  () => props.modelId,
  (newId) => {
    setModelId(newId);
  }
);

const { labels, isFetching, fetchNextPage, isFetchingNextPage, hasNextPage, search, setModelId } =
  useModelLabelsList();

// Set the modelId when component mounts and when it changes
onMounted(() => {
  if (props.modelId !== null && props.modelId !== undefined) {
    setModelId(props.modelId);
    resetInfititeScrollState();
  }
});
function resetInfititeScrollState() {
  if (setInfiniteScrollState.value) {
    setInfiniteScrollState.value("ok");
  }
}

watch(
  () => props.modelId,
  (newId) => {
    console.log("Model ID prop changed:", newId);
    if (newId !== null && newId !== undefined) {
      setModelId(newId);
      resetInfititeScrollState();
    }
  }
);

watch(search, () => {
  resetInfititeScrollState();
});
</script>

<template>
  <v-toolbar min-width="200">
    <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" density="compact" />
  </v-toolbar>
  <v-list>
    <v-list-item v-if="props.modelId === null || props.modelId === undefined">
      <v-list-item-title>Select a model</v-list-item-title>
    </v-list-item>
    <v-infinite-scroll
      :height="300"
      @load="
        async ({ done, side }) => {
          setInfiniteScrollState = done;
          console.log('useModelLabelsList @load: ', side);
          if (side === 'start') {
            return done('empty');
          }
          try {
            const res = await fetchNextPage();
            console.log('useModelLabelsList Fetch completed successfully', res);
            done(res.hasNextPage ? 'ok' : 'empty');
          } catch (error) {
            console.error('Error fetching next page:', error);
            done('error');
          }
        }
      "
    >
      <v-list-item
        v-for="label in labels"
        :key="label.id"
        :title="label.label.name"
        :subtitle="`${label.label.english} (${label.label.german})`"
      >
      </v-list-item>
      <template #empty>
        <v-divider></v-divider>
      </template>
    </v-infinite-scroll>
  </v-list>
</template>
