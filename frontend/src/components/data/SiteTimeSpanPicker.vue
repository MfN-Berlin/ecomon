<script lang="ts" setup>
const props = defineProps<{
  siteId: number;
}>();

const {
  data: firstAndLastRecordDate,
  refetch: refetchFirstAndLastRecordDate,
  isLoading: isLoadingFirstAndLastRecordDate
} = useSiteGetFirstAndLastRecordDate(props.siteId);

const selectedStartDateTime = defineModel<Date>("startDateTime");
const selectedEndDateTime = defineModel<Date>("endDateTime");
const rangeStart = computed(() => {
  return $dayjs(firstAndLastRecordDate.value?.[0]?.first_record_date).toDate();
});
const rangeEnd = computed(() => {
  return $dayjs(firstAndLastRecordDate.value?.[0]?.last_record_date).toDate();
});

onMounted(async () => {
  await refetchFirstAndLastRecordDate();
  if (rangeStart.value && rangeEnd.value) {
    selectedStartDateTime.value = rangeStart.value;
    selectedEndDateTime.value = rangeEnd.value;
  }
});

const { $dayjs } = useNuxtApp();
watch(rangeStart, (val) => {
  if (val) {
    selectedStartDateTime.value = val;
  }
});
watch(rangeEnd, (val) => {
  if (val) {
    selectedEndDateTime.value = val;
  }
});
</script>

<template>
  <CommonTimeSpanPicker
    v-if="!isLoadingFirstAndLastRecordDate && firstAndLastRecordDate && firstAndLastRecordDate.length > 0"
    v-bind="$attrs"
    v-model:start-date-time="selectedStartDateTime"
    v-model:end-date-time="selectedEndDateTime"
    :range-start-date-time="$dayjs(firstAndLastRecordDate?.[0]?.first_record_date).toDate()"
    :range-end-date-time="$dayjs(firstAndLastRecordDate?.[0]?.last_record_date).toDate()"
  />

  <v-skeleton-loader
    v-else
    class="mx-auto border"
    type="button@2, divider, list-item@2"
    elevation="0"
  ></v-skeleton-loader>
</template>
