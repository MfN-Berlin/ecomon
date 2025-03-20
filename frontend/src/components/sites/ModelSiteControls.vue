<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();

const { data: firstAndLastRecordDate, refetch } = useSiteGetFirstAndLastRecordDate(props.siteId);
const { data: modelList, isLoading: modelListLoading, refetch: refetchModelList } = useModelList();
const { mutate: startInference, isPending: startInferencePending } = useInferenceSiteTimespan();
const selectedModel = ref<number | null>(null);
const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());
const dialog = ref(false);

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
    startDatetime: selectedStartDateTime.value.toISOString(),
    endDatetime: selectedEndDateTime.value.toISOString()
  });
  dialog.value = false;
}
</script>

<template>
  <v-card :class="$attrs.class">
    <v-list>
      <v-list-subheader> Inference Panel </v-list-subheader>
      <v-toolbar flat density="compact" class="w-100" color="surface">
        <v-btn prepend-icon="mdi-eye" color="primary" @click="dialog = true"> Inference logs </v-btn>
        <v-spacer></v-spacer>
        <v-btn prepend-icon="mdi-brain" color="primary" variant="tonal" @click="dialog = true"
          >Start Inference</v-btn
        >
      </v-toolbar>
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
