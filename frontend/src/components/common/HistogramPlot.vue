<script setup lang="ts">
import { BasePlotly } from "#components";
import { computed } from "vue";

type HistogramData = {
  x: string[];
  y: number[];
};

const props = defineProps<{
  data?: HistogramData | null;
  title: string;
  xAxisLabel: string;
  yAxisLabel: string;
  maxY?: number;
  loading?: boolean;
}>();

const x = computed(() => props.data?.x ?? []);
const y = computed(() => props.data?.y ?? []);

const plotlyData = computed(() => {
  // OPTION 1: Actual counts (non‑normalized bar heights)
  // OPTION 2: Normalized values (each bar becomes a fraction of the max).
  // Uncomment the following line and adjust the annotation below if you prefer normalization.
  // const yValues = counts.map(c => c / maxCount);

  const trace = {
    type: "bar",
    x: x.value,
    y: y.value,
    marker: { color: "rgba(55,128,191,0.7)" },
    // Display the actual count (even when using normalized height, you might want
    // to show the original count using the text property)

    text: x.value,
    textposition: "auto"
  };

  return [trace];
});

const layout = computed(() => {
  if (!props.data) {
    return {
      title: props.title,
      xaxis: { title: props.xAxisLabel },
      yaxis: { title: props.yAxisLabel }
    };
  }

  const maxCount = Math.max(...y.value);
  const maxIndex = y.value.findIndex((count) => count === maxCount);

  return {
    title: props.title,
    xaxis: { title: props.xAxisLabel },
    yaxis: { title: props.yAxisLabel },
    // If you normalize the bar heights, you might want to set y: 1 here.
    annotations: [
      {
        x: x.value[maxIndex],
        y: maxCount, // Use "1" here if using normalization instead
        text: `Max: ${maxCount}`,
        showarrow: true,
        arrowhead: 7,
        ax: 0,
        ay: -30
      }
    ]
  };
});
</script>

<template>
  <v-container class="pa-1 pt-4">
    <base-plotly :data="plotlyData" :layout="layout" :loading="loading" />
  </v-container>
</template>
