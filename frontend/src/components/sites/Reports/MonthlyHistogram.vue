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
const { data, isLoading } = useGetSiteReportMonthlyHistogram(id);
watch(isLoading, (value) => {
  emit("update:loading", value);
});
const selectedData = computed(() => {
  if (!props.timePeriod || props.timePeriod == "All" || !data.value) {
    return data.value?.data.dates.reduce(
      (acc: { x: string[]; y: number[] }, date: string, index: number) => {
        acc.x.push(date);
        acc.y.push(data.value!.data.counts[index]);
        return acc;
      },
      { x: [], y: [] }
    );
  }
  return data.value?.data.dates.reduce(
    (acc: { x: string[]; y: number[] }, date: string, index: number) => {
      if (date.includes(props.timePeriod!)) {
        acc.x.push(date);
        acc.y.push(data.value!.data.counts[index]);
      }
      return acc;
    },
    {
      x: [],
      y: []
    }
  );
});

function downloadData() {
  const dataToDownload = selectedData.value;
  if (!dataToDownload || dataToDownload.length === 0) {
    console.warn("No data available for download.");
    return;
  }

  // Create CSV content from the data
  let csvContent = "Date,Count\n";

  for (let i = 0; i < dataToDownload.length; i++) {
    csvContent += `${dataToDownload.x[i]},${dataToDownload.y[i]}\n`;
  }

  // Create a Blob from the CSV content and generate a URL
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "monthly_histogram.csv";
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
  <v-container class="pa-1 pt-4">
    <common-histogram-plot
      :data="selectedData"
      title="Monthly Record Counts"
      x-axis-label="Date"
      y-axis-label="Count"
      :loading="isLoading"
    />
  </v-container>
</template>
