<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();

const { data: firstAndLastRecordDate, refetch } = useSiteGetFirstAndLastRecordDate(props.siteId);

const { mutate: startInference, isPending: startInferencePending } = useInferenceSiteTimespan();
const { $activeJobs, $dayjs } = useNuxtApp();
const activeJobs = computed(() =>
  $activeJobs.value?.jobs.filter(
    (job) => job.metadata.site_id === props.siteId && job.topic === "model_inference_site"
  )
);
const selectedModel = ref<number | null>(null);
const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const dialog = ref(false);
const { $currentTimeString } = useNuxtApp();

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

const firstRecordDate = computed(() => {
  if (!firstAndLastRecordDate.value || !firstAndLastRecordDate.value[0]) {
    return null;
  }
  return new Date(firstAndLastRecordDate.value[0].first_record_date);
});

const lastRecordDate = computed(() => {
  if (!firstAndLastRecordDate.value || !firstAndLastRecordDate.value[0]) {
    return null;
  }
  return new Date(firstAndLastRecordDate.value[0].last_record_date);
});

watch(dialog, (val) => {
  if (val) {
    refetch();
    refetchModelList();
    if (lastRecordDate.value && firstRecordDate.value) {
      selectedStartDateTime.value = firstRecordDate.value;
      selectedEndDateTime.value = lastRecordDate.value;
    }
    selectedModel.value = null;
  }
});
watch(firstAndLastRecordDate, (val) => {
  console.log("firstAndLastRecordDate", val);
  if (lastRecordDate.value && firstRecordDate.value) {
    selectedStartDateTime.value = firstRecordDate.value;
    selectedEndDateTime.value = lastRecordDate.value;
  }
});

function selectYear(year: number) {
  selectedStartDateTime.value = new Date(`${year}-01-01`);
  selectedStartDateTime.value.setHours(0, 0, 0, 0);
  selectedEndDateTime.value = new Date(`${year}-12-31`);
  selectedEndDateTime.value.setHours(23, 59, 59, 999);
}

async function onStartInference() {
  await startInference({
    siteId: props.siteId,
    modelId: selectedModel.value!,
    startDatetime: $dayjs(selectedStartDateTime.value).local().format("YYYY-MM-DDTHH:mm:ss"),
    endDatetime: $dayjs(selectedEndDateTime.value).local().format("YYYY-MM-DDTHH:mm:ss")
  });
  dialog.value = false;
}
</script>

<template>
  <v-card :class="$attrs.class">
    <v-list>
      <v-toolbar flat density="compact" class="w-100 pr-3" color="surface">
        <sites-inference-log :site-id="props.siteId"></sites-inference-log>
        <v-spacer></v-spacer>
        <v-btn prepend-icon="mdi-brain" color="primary" variant="tonal" @click="dialog = true"
          >Start Inference</v-btn
        >
      </v-toolbar>
      <v-list-subheader>Active Inference Jobs</v-list-subheader>
      <v-list-item v-for="job in activeJobs" :key="job.id">
        <sites-inference-info
          :id="job.id"
          :created-at="job.created_at"
          :updated-at="$currentTimeString"
          :model-name="modelNameById(job.metadata.model_id) ?? 'unkown'"
          :start-datetime="job.metadata.start_datetime"
          :end-datetime="job.metadata.end_datetime"
          :error="job.error"
          border
          class="pa-3"
          :status="job.status"
          :progress="job.progress"
        ></sites-inference-info>
      </v-list-item>
    </v-list>
  </v-card>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-toolbar class="px-4" color="primary" icon="mdi-brain">
        <v-icon icon="mdi-brain"></v-icon>
        <v-toolbar-title>Start Inference</v-toolbar-title>
      </v-toolbar>

      <v-card-text>
        <v-select
          v-model="selectedModel"
          prepend-inner-icon="mdi-brain"
          :items="modelList"
          item-title="name"
          item-value="id"
          label="Model"
          :loading="modelListLoading"
        />

        <CommonYearSelectBar
          class="mb-4"
          :start-date="firstRecordDate"
          :end-date="lastRecordDate"
          @select="selectYear"
        />

        <CommonDateTimePicker
          v-model="selectedStartDateTime"
          icon="mdi-calendar-start"
          prepend-inner-icon="mdi-calendar-start"
          dialog-title="Select Start Timestamp"
          label="Start Timestamp"
        />

        <CommonDateTimePicker
          v-model="selectedEndDateTime"
          icon="mdi-calendar-end"
          prepend-inner-icon="mdi-calendar-end"
          dialog-title="Select End Timestamp"
          label="End Timestamp"
        />
      </v-card-text>

      <v-card-actions>
        <v-btn prepend-icon="mdi-close" min-width="100" @click="dialog = false">Cancel</v-btn>
        <v-btn
          min-width="100"
          color="primary"
          variant="tonal"
          prepend-icon="mdi-play"
          :disabled="selectedModel === null"
          :loading="startInferencePending"
          @click="onStartInference"
          >Start
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
