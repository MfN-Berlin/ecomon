<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  reportId: number;
  timePeriod: string | null;
}>();

const emit = defineEmits<{
  (e: "update:loading", value: boolean): void;
}>();

const id = computed(() => props.reportId);
const { data, isLoading } = useGetSiteReportDurationHistogram(id);
watch(isLoading, (value) => {
  emit("update:loading", value);
});
const selectedData = computed(() => {
  console.log(data.value);
  const values = data.value?.data.reduce(
    (acc: any, item: { year: number; duration_range: number[]; count: number[] }) => {
      if ((props.timePeriod && `${item.year}` === props.timePeriod) || props.timePeriod === "All") {
        for (const [index, duration] of item.duration_range.entries()) {
          if (acc[duration]) {
            acc[duration] += item.count[index];
          } else {
            acc[duration] = item.count[index];
          }
        }
      }
      return acc;
    },
    {}
  );
  return Object.entries(values || {}).map(([key, value]) => ({
    duration: key,
    count: value
  }));
});

const headers = [
  { title: "Duration (s)", key: "duration", sortable: true },
  { title: "Count", key: "count", sortable: true }
] as const;

// Function to download the selected data as a CSV file
function downloadData() {
  const dataToDownload = selectedData.value;
  if (!dataToDownload || dataToDownload.length === 0) {
    console.warn("No data available for download.");
    return;
  }

  // Create CSV content from the data
  let csvContent = "Duration (s),Count\n";
  csvContent += dataToDownload.map((item) => `${item.duration},${item.count}`).join("\n");

  // Create a Blob from the CSV content and generate a URL
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "duration_histogram.csv";
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
  <v-container>
    <v-data-table :headers="headers" :items="selectedData" hide-default-footer></v-data-table>
    <v-progress-linear v-if="isLoading" indeterminate />
  </v-container>
</template>
