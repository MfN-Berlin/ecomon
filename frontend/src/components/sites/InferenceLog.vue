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
    <v-dialog v-model="open" width="auto" max-width="800px" activator="parent">
      <v-card class="h-75">
        <v-toolbar color="primary" class="px-4">
          <v-icon icon="mdi-eye"></v-icon>
          <v-toolbar-title>Inference Log</v-toolbar-title>
        </v-toolbar>

        <v-card-text class="h-75 overflow-y-auto">
          <v-timeline class="h-75 mr-6" align="start" side="end">
            <v-timeline-item
              v-for="log in logs"
              :key="log.id"
              :dot-color="log.error ? 'error' : 'primary'"
              :icon="log.error ? 'mdi-alert' : 'mdi-check'"
              size="small"
            >
              <v-sheet
                elevation="1"
                class="pa-2 flex-grow-1"
                :color="log.error ? 'red-lighten-5' : 'green-lighten-5'"
              >
                <v-row no-gutters class="mb-3">
                  <common-date-time-text
                    class="me-4"
                    :time="log.created_at"
                    size="small"
                  ></common-date-time-text>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="12" md="12">
                    <v-text-field
                      label="Model"
                      class="flex-grow-1"
                      prepend-inner-icon="mdi-brain"
                      disabled
                      variant="outlined"
                      density="compact"
                      :model-value="modelNameById(log.metadata?.model_id)"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      class="pr-1"
                      label="Start Datetime"
                      prepend-inner-icon="mdi-calendar-start"
                      disabled
                      variant="outlined"
                      density="compact"
                      :model-value="log.metadata?.start_datetime"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      class="pl-1"
                      label="End Datetime"
                      prepend-inner-icon="mdi-calendar-end"
                      disabled
                      variant="outlined"
                      density="compact"
                      :model-value="log.metadata?.end_datetime"
                    ></v-text-field>
                  </v-col>
                  <v-col v-if="!log.error" cols="12" md="12" class="pl-2">
                    Analysed Records:
                    <span class="font-weight-bold">{{ log.result?.inferred_records }}</span>
                  </v-col>
                  <v-col v-else cols="12" md="12" class="pl-2">
                    Error:
                    <span class="font-weight-bold">{{ log.error }}</span>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-timeline-item>
          </v-timeline>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="open = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>
