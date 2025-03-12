<script setup lang="ts">
import type { SiteFragment } from "#gql";
import dayjs from "dayjs";

const props = defineProps<{
  reportId: number;
  site: SiteFragment;
}>();

const id = computed(() => props.reportId);
const { data: report, isLoading: reportLoading } = useGetSiteReportById(id);

const timePeriods = computed(() => {
  if (report.value?.first_record_date && report.value?.last_record_date) {
    // ad missing yeats in betweeen
    const startYear = dayjs(report.value.first_record_date).year();
    const endYear = dayjs(report.value.last_record_date).year();
    const diff = endYear - startYear + 1;
    const yearsArray = Array.from({ length: diff }, (_, i) => `${endYear - i}`);
    yearsArray.push("All");
    return yearsArray;
  }
  return [];
});

const DiagramTypes = [
  { value: "monthly", title: "Monthly Record Counts" },
  { value: "daily", title: "Daily Record Counts" },
  { value: "duration", title: "Record Durations" },
  { value: "heatmap", title: "Records Heatmap" }
] as const;
const diagramType = ref<string>("monthly");
const timePeriod = ref<string | null>(null);

watch(
  timePeriods,
  (newVal) => {
    if (newVal.length > 0) {
      timePeriod.value = newVal[0];
    }
  },
  { immediate: true }
);
// Watch the reports computed for changes and auto-select the first report once it's loaded.
const downloadComponent = ref<any>([]);
function downloadData() {
  downloadComponent.value.downloadData();
}
const isLoading = ref(false);

watch(reportLoading, (value) => {
  isLoading.value = value;
});

function updateLoading(value: boolean) {
  isLoading.value = value;
}
</script>

<template>
  <v-toolbar color="surface" density="compact">
    <div class="pl-2 pt-5" style="width: 180px">
      <v-select
        v-model="diagramType"
        density="compact"
        variant="solo"
        :items="DiagramTypes"
        label="Diagram Type"
      />
    </div>
    <div class="pl-2 pt-5" style="width: 180px">
      <v-select
        v-model="timePeriod"
        density="compact"
        variant="solo"
        :items="timePeriods"
        label="Time Period"
      />
    </div>
    <v-spacer />
    <v-btn icon="mdi-download" variant="text" @click="downloadData" />
  </v-toolbar>
  <template v-if="id">
    <sites-reports-daily-histogram
      v-if="diagramType === 'daily'"
      ref="downloadComponent"
      :reportId="id"
      :timePeriod="timePeriod"
      @update:loading="updateLoading"
    />
    <sites-reports-monthly-histogram
      v-if="diagramType === 'monthly'"
      ref="downloadComponent"
      :reportId="id"
      :timePeriod="timePeriod"
      @update:loading="updateLoading"
    />
    <sites-reports-duration-list
      v-if="diagramType === 'duration'"
      ref="downloadComponent"
      :reportId="id"
      :timePeriod="timePeriod"
      @update:loading="updateLoading"
    />
    <sites-reports-record-heatmap
      v-if="diagramType === 'heatmap'"
      ref="downloadComponent"
      :reportId="id"
      :timePeriod="timePeriod"
      :startYear="dayjs(report?.first_record_date).year()"
      :endYear="dayjs(report?.last_record_date).year()"
      :timeStepSeconds="site.record_regime_recording_duration + site.record_regime_pause_duration"
      @update:loading="updateLoading"
    />
  </template>
  <div v-else>
    <v-skeleton-loader type="image" />
    <v-skeleton-loader type="table-row" />
  </div>
  <v-progress-linear v-if="isLoading" indeterminate />
</template>
