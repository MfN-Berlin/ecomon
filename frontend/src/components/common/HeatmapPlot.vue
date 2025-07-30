<script setup lang="ts">
import { BasePlotly } from "#components";
import { computed } from "vue";

type HeatMapData = number[][];

type ColorRange = [number, string];
type ColorBar = {
  title: string;
  tickmode: "auto" | "manual" | "array";
  tickvals: number[];
  ticktext: string[];
};
const props = defineProps<{
  data?: HeatMapData | null;
  title: string;
  xAxis: string[];
  yAxis: string[];
  xAxisLabel: string;
  yAxisLabel: string;
  maxY?: number;
  loading?: boolean;
  transpose?: boolean;
  colorScale?: ColorRange[];
  zmin?: number;
  zmax?: number;
  colorBar?: ColorBar;
  hideHover?: boolean; 
}>();

const plotlyData = computed(() => {
  if (!props.data) {
    return [];
  }

  const heatmapTrace = {
    type: "heatmap",
    x: props.xAxis,
    y: props.yAxis,
    z: props.transpose ? transposeFunction(props.data) : props.data,
    colorscale: props.colorScale ?? "Viridis",
    zmin: props.zmin,
    zmax: props.zmax,
    colorbar: props.colorBar,
    // hoverongaps: false,
    hoverInfo: 'none'
  };

  return [heatmapTrace];
});

function transposeFunction(mat: number[][]) {
  //create Array of with
  const trans = [];
  for (let i = 0; i < mat[0].length; i++) {
    const row = [];
    for (let j = 0; j < mat.length; j++) {
      row.push(mat[j][i]);
    }
    trans.push(row);
  }
  return trans;
}

const layout = computed(() => {
  const baseLayout = {
    title: props.title,
    xaxis: {
      title: props.xAxisLabel
    },
    yaxis: {
      title: props.yAxisLabel
    }
  };

  if (props.hideHover) {
    return {
      ...baseLayout,
      hovermode: false
    };
  }

  return baseLayout;
});
</script>

<template>
  <v-container class="pa-1 pt-4">
    <base-plotly :data="plotlyData" :layout="layout" :loading="loading" :hideHover="props.hideHover"/>
  </v-container>
</template>
