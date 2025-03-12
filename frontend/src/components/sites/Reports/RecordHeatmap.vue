<script setup lang="ts">
import type { SiteFragment } from "#gql";

const props = defineProps<{
  reportId: number;
  startYear: number;
  endYear: number;
  timeStepSeconds: number;
  timePeriod: string | null;
}>();

const emit = defineEmits<{
  (e: "update:loading", value: boolean): void;
}>();

const colorScale = [
  [0, "red"],
  [0.33, "red"],
  [0.33, "white"],
  [0.66, "white"],
  [0.66, "green"],
  [1, "green"]
];

const colorBar = {
  title: "Records",
  tickmode: "array",
  tickvals: [-0.66, 0, 0.66],
  ticktext: ["error", "no record", "valid record"]
};

const id = computed(() => props.reportId);
const { data, isLoading } = useGetSiteReportRecordsHeatmap(id);

watch(isLoading, (value) => {
  emit("update:loading", value);
});

const dates = computed(() => generateDayDatesForYearRange(props.startYear, props.endYear));
const times = computed(() => generateTimeArray(props.timeStepSeconds));
const selectedData = computed(() => {
  if (!props.timePeriod || props.timePeriod == "All" || !data.value) {
    const tmp = data.value?.data;
    if (tmp) {
      if (tmp.length < dates.value.length) {
        console.log("tmp.length < dates.value.length");
        return tmp.concat(Array(dates.value.length - tmp.length).fill(Array(times.value.length).fill(0)));
      }
    }

    return tmp;
  }
  // calculate year start index
  const yearsDayCounts = generateYearsDayCountsArray(props.startYear, props.endYear);
  const selectedYear = parseInt(props.timePeriod!);
  const selectedYearCountsIndex = selectedYear - props.startYear;
  const yearStartIndex = range(selectedYearCountsIndex).reduce((acc, curr) => acc + yearsDayCounts[curr], 0);
  // calculate year end index
  const selectedData = data.value?.data.slice(
    yearStartIndex,
    yearStartIndex + yearsDayCounts[selectedYearCountsIndex]
  );

  return selectedData;
});
function downloadData() {
  const dataToDownload = selectedData.value;
  if (!dataToDownload || dataToDownload.length === 0) {
    console.warn("No data available for download.");
    return;
  }

  // Create CSV content from the data
  let csvContent = "time," + dates.value.join(",") + "\n" + dataToDownload.y.join(",");
  if (data && data.value)
    for (let i = 0; i < dataToDownload.length; i++) {
      csvContent += times.value[i] + "," + data.value.data[i].join(",");
    }

  // Create a Blob from the CSV content and generate a URL
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "record_heatmap.csv";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Expose the downloadData function so it can be called on this component instance
defineExpose({
  downloadData
});
</script>

<template>
  <v-container v-if="selectedData" class="pa-1 pt-4">
    <common-heatmap-plot
      :data="selectedData"
      :x-axis="dates"
      :y-axis="times"
      title="Records Heatmap"
      x-axis-label="Date"
      y-axis-label="Time"
      :transpose="true"
      :color-scale="colorScale"
      :color-bar="colorBar"
      :zmin="-1"
      :zmax="1"
    />
  </v-container>
</template>
