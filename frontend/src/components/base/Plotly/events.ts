import type Plotly from "plotly.js-dist-min";

export type PlotlyEventPayloads = {
  plotly_click: Plotly.PlotMouseEvent;
  plotly_hover: Plotly.PlotHoverEvent;
  plotly_unhover: Plotly.PlotMouseEvent;
  plotly_selecting: Plotly.PlotSelectionEvent;
  plotly_selected: Plotly.PlotSelectionEvent;
  plotly_restyle: Plotly.PlotRestyleEvent;
  plotly_relayout: Plotly.PlotRelayoutEvent;
  plotly_clickannotation: Plotly.ClickAnnotationEvent;
  plotly_legendclick: Plotly.LegendClickEvent;
  plotly_legenddoubleclick: Plotly.LegendClickEvent;
  plotly_sliderchange: Plotly.SliderChangeEvent;
  plotly_sliderend: Plotly.SliderEndEvent;
  plotly_sliderstart: Plotly.SliderStartEvent;
  plotly_sunburstclick: Plotly.SunburstClickEvent;
  plotly_beforeplot: Plotly.BeforePlotEvent;
};

export type CombinedPlotlyEvent = {
  [K in keyof PlotlyEventPayloads]: PlotlyEventPayloads[K] extends void
    ? { event: K }
    : { event: K; payload: PlotlyEventPayloads[K] };
}[keyof PlotlyEventPayloads];

export const events = [
  "plotly_click",
  "plotly_hover",
  "plotly_unhover",
  "plotly_selecting",
  "plotly_selected",
  "plotly_restyle",
  "plotly_relayout",
  "plotly_relayouting",
  "plotly_clickannotation",
  "plotly_animatingframe",
  "plotly_legendclick",
  "plotly_legenddoubleclick",
  "plotly_sliderchange",
  "plotly_sliderend",
  "plotly_sliderstart",
  "plotly_sunburstclick",
  "plotly_event",
  "plotly_beforeplot",
  "plotly_afterexport",
  "plotly_afterplot",
  "plotly_animated",
  "plotly_animationinterrupted",
  "plotly_autosize",
  "plotly_beforeexport",
  "plotly_deselect",
  "plotly_doubleclick",
  "plotly_framework",
  "plotly_redraw",
  "plotly_transitioning",
  "plotly_transitioninterrupted"
];

export default events;
