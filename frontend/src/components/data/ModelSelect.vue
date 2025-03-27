<script lang="ts" setup>
const selectedModel = defineModel<number | null>();

const { data: modelList, isLoading: modelListLoading, refetch: refetchModelList } = useModelList();

onMounted(async () => {
  refetchModelList();
  selectedModel.value = null;
});
</script>

<template>
  <v-select
    v-model="selectedModel"
    prepend-inner-icon="mdi-brain"
    :items="modelList"
    item-title="name"
    item-value="id"
    label="Model"
    :loading="modelListLoading"
  />
</template>
