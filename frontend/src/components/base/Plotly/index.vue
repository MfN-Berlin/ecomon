<script setup lang="ts">
import { nanoid } from "nanoid";
import Plotly from "plotly.js-dist-min";
import { onBeforeUnmount, ref, watchEffect } from "vue";

import { events, type CombinedPlotlyEvent } from "./events";

const props = defineProps<{
  data?: Plotly.Data[];
  layout?: Partial<Plotly.Layout>;
  config?: Partial<Plotly.Config>;
  loading?: boolean;
}>();

const emit = defineEmits(events);
const configWithDefaults = computed(() => {
  return {
    ...props.config,
    toImageButtonOptions: {
      format: "svg" as const,
      filename: "plotly-export"
    }
  };
});

const plotlyId = ref<string>(`plotly-${nanoid()}`);
const divRef = ref<Plotly.PlotlyHTMLElement>();

let isCreated = false;

function resize() {
  Plotly.Plots.resize(divRef.value as Plotly.Root);
}

const resizeDebounced = useDebounceFn(resize, 50);

const resizeObserver = new ResizeObserver(resizeDebounced);

function setPlotlyEventHandlers() {
  const div = divRef.value as Plotly.PlotlyHTMLElement;

  for (const event of events) {
    div.removeAllListeners(event);
  }

  div.on("plotly_click", (e: Plotly.PlotMouseEvent) => {
    emit("plotly_click", e);
  });
  div.on("plotly_hover", (e: Plotly.PlotHoverEvent) => {
    emit("plotly_hover", e);
  });
  div.on("plotly_unhover", (e: Plotly.PlotMouseEvent) => {
    emit("plotly_unhover", e);
  });
  div.on("plotly_selecting", (e: Plotly.PlotSelectionEvent) => {
    emit("plotly_selecting", e);
  });
  div.on("plotly_selected", (e: Plotly.PlotSelectionEvent) => {
    emit("plotly_selected", e);
  });
  div.on("plotly_restyle", (e: Plotly.PlotRestyleEvent) => {
    emit("plotly_restyle", e);
  });
  div.on("plotly_relayout", (e: Plotly.PlotRelayoutEvent) => {
    emit("plotly_relayout", e);
  });
  div.on("plotly_clickannotation", (e: Plotly.ClickAnnotationEvent) => {
    emit("plotly_clickannotation", e);
  });
  div.on("plotly_legendclick", (e: Plotly.LegendClickEvent) => {
    emit("plotly_legendclick", e);
    return true;
  });
  div.on("plotly_legenddoubleclick", (e: Plotly.LegendClickEvent) => {
    emit("plotly_legenddoubleclick", e);
    return true;
  });
  div.on("plotly_sliderchange", (e: Plotly.SliderChangeEvent) => {
    emit("plotly_sliderchange", e);
  });
  div.on("plotly_sliderend", (e: Plotly.SliderEndEvent) => {
    emit("plotly_sliderend", e);
  });
  div.on("plotly_sliderstart", (e: Plotly.SliderStartEvent) => {
    emit("plotly_sliderstart", e);
  });
  div.on("plotly_sunburstclick", (e: Plotly.SunburstClickEvent) => {
    emit("plotly_sunburstclick", e);
  });
  div.on("plotly_event", (e: CombinedPlotlyEvent) => {
    emit("plotly_event", e);
  });
  div.on("plotly_beforeplot", (e: Plotly.BeforePlotEvent) => {
    emit("plotly_beforeplot", e);
    return true;
  });
  div.on("plotly_afterexport", () => {
    emit("plotly_afterexport");
  });
  div.on("plotly_afterplot", () => {
    emit("plotly_afterplot");
  });
  div.on("plotly_animated", () => {
    emit("plotly_animated");
  });
  div.on("plotly_animationinterrupted", () => {
    emit("plotly_animationinterrupted");
  });
  div.on("plotly_autosize", () => {
    emit("plotly_autosize");
  });
  div.on("plotly_beforeexport", () => {
    emit("plotly_beforeexport");
  });
  div.on("plotly_deselect", () => {
    emit("plotly_deselect");
  });
  div.on("plotly_doubleclick", () => {
    emit("plotly_doubleclick");
  });
  div.on("plotly_framework", () => {
    emit("plotly_framework");
  });
  div.on("plotly_redraw", () => {
    emit("plotly_redraw");
  });
  div.on("plotly_transitioning", () => {
    emit("plotly_transitioning");
  });
  div.on("plotly_transitioninterrupted", () => {
    emit("plotly_transitioninterrupted");
  });
}

watchEffect(async () => {
  const data = props.data ? props.data : [];
  const div = divRef.value as Plotly.Root;
  if (isCreated) {
    Plotly.react(div, data, props.layout, configWithDefaults.value);
  } else if (div) {
    await Plotly.newPlot(div, data, props.layout, configWithDefaults.value);
    resizeObserver.observe(div as Plotly.PlotlyHTMLElement);
    setPlotlyEventHandlers();
    isCreated = true;
  }
});

onBeforeUnmount(() => {
  resizeObserver.disconnect();
  Plotly.purge(divRef.value as Plotly.Root);
});

defineExpose({ plotlyId, setPlotlyEventHandlers });
</script>

<template>
  <div :id="plotlyId" ref="divRef"></div>
  <v-progress-linear v-if="loading" indeterminate />
</template>
