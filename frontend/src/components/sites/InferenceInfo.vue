<script setup lang="ts">
const props = defineProps<{
  id: number;
  createdAt: string;
  updatedAt?: string;
  finishedAt?: string;
  modelName: string;
  startDatetime?: string;
  endDatetime?: string;
  error?: unknown;
  inferredRecords?: number;
  status?: "pending" | "running" | "finished" | "failed";
  progress?: number;
}>();
const { $dayjs } = useNuxtApp();
const { openDialog } = useDialogStore();
const { mutate: cancelJob } = useCancelJob();
const durationHumanReadable = computed(() => {
  if (props.finishedAt) {
    return $dayjs(props.finishedAt || props.updatedAt).diff(props.createdAt, "minutes");
  }
  return 0;
});
</script>

<template>
  <v-sheet v-bind="$attrs">
    <v-row dense class="pb-3 align-center">
      <common-date-time-text
        class="me-4"
        :time="props.createdAt"
        size="small"
        icon="mdi-ray-start"
      ></common-date-time-text>
      <common-date-time-text
        v-if="props.finishedAt"
        class="me-4"
        :time="props.finishedAt"
        size="small"
        icon="mdi-ray-end"
      ></common-date-time-text>
      <div v-if="props.finishedAt || props.updatedAt">
        <v-tooltip :text="`Cancel Inference Job`" location="top">
          <template #activator="{ props: tooltipProps }">
            <v-progress-circular
              v-if="props.status === 'running' || props.status === 'pending'"
              v-bind="tooltipProps"
              class="mr-1"
              color="secondary"
              :indeterminate="props.status === 'pending'"
              :model-value="props.progress || 0"
            >
              <v-btn
                icon="mdi-clock-outline"
                size="small"
                variant="text"
                v-bind="tooltipProps"
                @click="
                  openDialog(
                    `Cancel Job`,
                    `Are you sure you want to cancel inference job with model ${props.modelName}?`,
                    async () => await cancelJob({ jobId: id })
                  )
                "
              />
            </v-progress-circular>
          </template>
        </v-tooltip>
      </div>
      <v-icon v-else class="mr-1" icon="mdi-clock-fast" size="small"></v-icon>
      <span class="text-caption">{{ durationHumanReadable }} minutes </span>
    </v-row>
    <v-row dense>
      <v-col cols="12" md="4">
        <v-text-field
          label="Model"
          class="flex-grow-1"
          prepend-inner-icon="mdi-brain"
          disabled
          variant="outlined"
          density="compact"
          :model-value="props.modelName"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          label="Start Datetime"
          prepend-inner-icon="mdi-calendar-start"
          disabled
          variant="outlined"
          density="compact"
          :model-value="props.startDatetime"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          label="End Datetime"
          prepend-inner-icon="mdi-calendar-end"
          disabled
          variant="outlined"
          density="compact"
          :model-value="props.endDatetime"
        ></v-text-field>
      </v-col>
      <v-col v-if="props.inferredRecords" cols="12" md="12" class="pl-2 text-caption">
        Analysed Records:
        <span class="font-weight-bold">{{ props.inferredRecords }}</span>
      </v-col>
      <v-col v-if="props.error" cols="12" md="12" class="pl-2 text-caption">
        Error:
        <span class="font-weight-bold">{{ props.error }}</span>
      </v-col>
    </v-row>
  </v-sheet>
</template>
