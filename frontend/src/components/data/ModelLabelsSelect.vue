<script lang="ts" setup>
import { onMounted, watch, ref } from "vue";

import useModelLabelsList from "@/composables/api/useModelLabelsList";
import type { Label } from "@/composables/api/useModelLabelsList";

const props = defineProps<{
  modelId?: number | null;
}>();

type DoneType = ((state: "ok" | "empty" | "error") => void) | null;
const selectedLabels = defineModel<Label[]>("selectedLabels", { default: [] });

const selectAll = defineModel<boolean>("selectAll", { default: false });
const setInfiniteScrollState = ref<DoneType>(null);
watch(
  () => props.modelId,
  (newId) => {
    setModelId(newId);
  }
);

const { labels, fetchNextPage, search, setModelId } = useModelLabelsList();

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
const { checkModelLabels, loading: checkModelLabelsLoading } = useCheckModelLabels();
watch(
  () => props.modelId,
  async (newId) => {
    if (newId !== null && newId !== undefined) {
      // Model ID changed, check if the selected labels exist in the model
      const result = await checkModelLabels(
        newId,
        selectedLabels.value.map((l) => l.id)
      );
      const filteredLabels = selectedLabels.value.filter((l, index) => result[index]);
      selectedLabels.value = filteredLabels;
    }
    // Model ID changed, set the modelId and reset the infinite scroll state
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
  <div class="d-flex flex-row">
    <v-text-field
      v-model="search"
      class="flex-grow-1 mr-4"
      varian="solo"
      prepend-inner-icon="mdi-magnify"
      density="compact"
    />

    <v-switch
      v-model="selectAll"
      class="flex-grow-0"
      color="secondary"
      density="compact"
      label="Select All"
    />
  </div>
  <div class="d-flex flex-wrap">
    <v-chip v-if="selectAll" class="ma-1" closable @click:close="selectAll = false"
      >All labels selected</v-chip
    >
    <v-chip
      v-for="label in selectedLabels"
      :key="label.id"
      class="ma-1"
      closable
      :disabled="selectAll || checkModelLabelsLoading"
      :loading="checkModelLabelsLoading"
      @click:close="selectedLabels = selectedLabels.filter((l) => l !== label)"
    >
      {{ label.name }}
    </v-chip>
  </div>
  <v-list>
    <v-list-item v-if="props.modelId === null || props.modelId === undefined">
      <v-list-item-title>Select a model</v-list-item-title>
    </v-list-item>

    <v-infinite-scroll
      :height="400"
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
      <v-item-group v-model="selectedLabels" multiple>
        <v-item
          v-for="label in labels.map((l) => l.label)"
          v-slot="{ isSelected, toggle, selectedClass }"
          :key="label.id"
          :value="label"
        >
          <v-list-item
            :class="'cursor-pointer' + '' + selectedClass"
            :title="label.name"
            :subtitle="`${label.english} (${label.german}) ${isSelected}`"
            @click="toggle"
          >
            <template #append>
              <v-checkbox :model-value="isSelected" :disabled="selectAll" density="compact"></v-checkbox>
            </template>
          </v-list-item>
        </v-item>
      </v-item-group>
      <template #empty>
        <v-divider></v-divider>
      </template>
    </v-infinite-scroll>
  </v-list>
</template>
