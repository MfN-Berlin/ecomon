<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();
const open = ref(false);
const { data: logs, refetch } = useGetSiteJobsByTopic({
  siteId: props.siteId,
  _or: [{ topic: { _eq: "model_inference_site" } }]
});

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
    refetchModelList();
  }
});
</script>

<template>
  <v-btn prepend-icon="mdi-eye" color="primary">
    Inference logs
    <v-dialog v-model="open" max-width="800px" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-eye"></v-icon>
          <v-toolbar-title>Inference Log</v-toolbar-title>
        </v-toolbar>

        <v-card-text class="h-75 overflow-y-auto">
          <v-list>
            <v-list-item v-for="log in logs" :key="log.id">
              <template #prepend>
                <v-icon
                  :icon="log.error ? 'mdi-alert' : 'mdi-check'"
                  :color="log.error ? 'error' : 'primary'"
                ></v-icon>
              </template>
              <sites-inference-info
                :id="log.id"
                :created-at="log.created_at"
                :finished-at="log.updated_at"
                :model-name="modelNameById(log.metadata?.model_id) ?? 'unkown'"
                :start-datetime="log.metadata?.start_datetime"
                :end-datetime="log.metadata?.end_datetime"
                :inferred-records="log.result?.inferred_records"
                :error="log.error"
              ></sites-inference-info>
              <v-divider></v-divider>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
