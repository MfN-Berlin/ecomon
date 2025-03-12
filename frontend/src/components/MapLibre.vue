<script setup lang="ts">
import maplibregl from "maplibre-gl";

onMounted(() => {
  const map = new maplibregl.Map({
    container: "map",
    style: {
      version: 8,
      sources: {
        "raster-tiles": {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256
        }
      },
      layers: [
        {
          id: "simple-tiles",
          type: "raster",
          source: "raster-tiles",
          minzoom: 0,
          maxzoom: 22
        }
      ]
    },
    center: [-95, 40],
    zoom: 4
  });

  map.addControl(new maplibregl.NavigationControl());
  map.addControl(new maplibregl.FullscreenControl());
});
</script>
<template>
  <div id="map"></div>
</template>

<style scoped>
#map {
  height: 220px;
  width: 320px;
}
</style>
