<script setup lang="ts">
const props = defineProps<{
  siteId: number;
}>();

const { data: firstAndLastRecordDate, refetch } = useSiteGetFirstAndLastRecordDate(props.siteId);

const { $dayjs } = useNuxtApp();

const selectedStartDateTime = ref<Date>(new Date());
const selectedEndDateTime = ref<Date>(new Date());

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
</script>

<template>
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
</template>
