<script lang="ts" setup>
import { loggers } from "winston";

const props = defineProps<{
  siteId: number;
}>();
const open = ref(false);
const { data: modelList, isLoading: modelListLoading, refetch: refetchModelList } = useModelList();

const modelIdMap = computed(() => {
  return modelList.value?.reduce(
    (acc, model) => {
      acc[model.id] = model.name;
      return acc;
    },
    {} as Record<number, string>
  );
});

const modelNameById = computed(() => {
  return (id: number) => modelIdMap.value?.[id];
});
watch(open, (val) => {
  if (val) {
    refetch();
  }
});
</script>

<template>
  <v-btn v-bind="$attrs" prepend-icon="mdi-eye">
    Create Voucher
    <v-dialog v-model="open" width="auto" max-width="800px" class="h-75" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-eye"></v-icon>
          <v-toolbar-title>Create Voucher</v-toolbar-title>
        </v-toolbar>
        <v-card-text class="h-75 overflow-y-auto"> </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
