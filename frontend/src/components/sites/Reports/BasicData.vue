<script setup lang="ts">
import dayjs from "dayjs";

const props = defineProps<{
  reportId: number;
}>();

const id = computed(() => props.reportId);

const { data: report, isLoading } = useGetSiteReportById(id);

const items = computed(() => [
  {
    icon: "mdi-calendar-start",
    title: "First Record",
    value: report && report.value ? dayjs(report?.value?.first_record_date).format("YYYY-MM-DD HH:mm") : "N/A"
  },
  {
    icon: "mdi-calendar-end",
    title: "Last Record",
    value: report && report.value ? dayjs(report?.value?.last_record_date).format("YYYY-MM-DD HH:mm") : "N/A"
  },
  {
    icon: "mdi-counter",
    title: "Record Count",
    value: report && report.value ? report?.value?.records_count : "N/A"
  },
  {
    icon: "mdi-timer",
    title: "Records Duration",
    value: report && report.value ? report?.value?.record_duration : "N/A"
  },
  {
    icon: "mdi-image-broken",
    title: "Corrupted Record Count",
    value: report && report.value ? report?.value?.corrupted_files?.length : "N/A"
  }
]);
</script>

<template>
  <v-container class="pa-1 pt-4">
    <v-row no-gutters>
      <v-col v-for="item in items" :key="item.title" cols="6" md="4">
        <v-text-field
          class="mx-1"
          :label="item.title"
          :prepend-inner-icon="item.icon"
          density="compact"
          variant="outlined"
          disabled
          :model-value="item.value"
        />
      </v-col>
    </v-row>
    <v-progress-linear v-if="isLoading" indeterminate></v-progress-linear>
  </v-container>
</template>
