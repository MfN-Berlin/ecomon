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
  const yearsDayCounts = generateYearsDayCountsArray(props.startYear, props.endYear);
  let selectedYear;
  let selectedYearCountsIndex;
  let yearStartIndex;
  let endIndex;
  if (!props.timePeriod || props.timePeriod == "All" || !data.value) {
    selectedYear = props.startYear;
    selectedYearCountsIndex = 0;
    yearStartIndex = 0;
    endIndex = dates.value.length - 1;
  } else {
    // calculate year start index

    selectedYear = parseInt(props.timePeriod!);
    selectedYearCountsIndex = selectedYear - props.startYear;
    yearStartIndex = range(selectedYearCountsIndex).reduce((acc, curr) => acc + yearsDayCounts[curr], 0);
    endIndex = yearStartIndex + yearsDayCounts[selectedYearCountsIndex] - 1;
  }

  console.log("yearsDayCounts", yearsDayCounts);
  console.log("yearStartIndex", yearStartIndex);

  console.log("endIndex", endIndex);
  console.log("dates.value.length", dates.value.length);
  // calculate year end index

  return {
    data: data.value?.data.slice(yearStartIndex, endIndex + 1),
    xAxis: dates.value.slice(yearStartIndex, endIndex + 1),
    yAxis: times.value
  };
});
function downloadData(siteId: number, year: string) {
  const dataToDownload = selectedData.value;
  if (!dataToDownload || dataToDownload.data.length === 0) {
    console.warn("No data available for download.");
    return;
  }

  // Create CSV content from the data
  let csvContent = "time," + dates.value.join(",") + "\n" + dataToDownload.yAxis.join(",");
  if (data && data.value)
    for (let i = 0; i < dataToDownload.data.length; i++) {
      csvContent += times.value[i] + "," + dataToDownload.data[i].join(",");
    }

  // Create a Blob from the CSV content and generate a URL
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = `record_heatmap_${siteId}_${year}.csv`;
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
      :data="selectedData.data"
      :x-axis="selectedData.xAxis"
      :y-axis="selectedData.yAxis"
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
