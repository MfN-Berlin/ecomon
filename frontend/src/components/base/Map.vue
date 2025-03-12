<script setup lang="ts">
import type { LngLatLike, StyleSpecification } from "maplibre-gl";
import maplibregl from "maplibre-gl";
import { onMounted, ref, watch, computed } from "vue";

/**
 * A simple style object using OpenStreetMap as a raster source.
 * The OSM tile server is used below. Be mindful of usage guidelines:
 * https://operations.osmfoundation.org/policies/tiles/
 */

type Marker = {
  id: string | number;
  name?: string;
  lat?: number | null;
  long?: number | null;
  color?: string;
  to?: string;
};

const props = withDefaults(
  defineProps<{
    markers: Marker[];
    defaultColor?: string;
    animate?: boolean;
  }>(),
  {
    markers: () => [],
    defaultColor: () => "#cc0000",
    animate: () => false
  }
);

const { markers, defaultColor, animate } = toRefs(props);

const mapRef = ref(null);

const osmStyle: StyleSpecification = {
  version: 8,
  sources: {
    osmTiles: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256
    }
  },
  layers: [
    {
      id: "osm-tiles",
      type: "raster",
      source: "osmTiles"
    }
  ]
};

/**
 * Create a computed array of coordinates:
 */
const boundingData = computed(() => {
  const coords = markers.value.filter((m) => m.lat && m.long).map((m) => [m.long, m.lat] as [number, number]);
  if (!coords.length) {
    return {
      coords,
      bounds: null
    };
  }

  const bounds = coords.reduce(
    (acc, coord) => acc.extend(coord),
    new maplibregl.LngLatBounds(coords[0], coords[0])
  );

  return {
    coords,
    bounds
  };
});

/**
 * Watch the bounding box for changes. Whenever it changes (or on first mount),
 * fit the map to the bounding box.
 */
watch(
  () => boundingData.value.bounds,
  (newBounds) => {
    if (!mapRef.value?.map || !newBounds) return;
    mapRef.value.map.fitBounds(newBounds, {
      padding: 40,
      maxZoom: 15,
      animate: animate.value
    });
  },
  { immediate: true }
);

const getCoordinates = computed(() => (marker: Marker) => {
  if (!marker.lat || !marker.long) return null;
  return { lat: marker.lat, lng: marker.long } as LngLatLike;
});

/**
 * Also use onMounted to re-center after the map has fully initialized.
 * This helps if the component remains cached in memory on route changes.
 */
onMounted(() => {
  if (!mapRef.value?.map || !boundingData.value.bounds) return;
  mapRef.value.map.fitBounds(boundingData.value.bounds, {
    padding: 80,
    maxZoom: 10,
    animate: animate.value
  });
});
</script>
<template>
  <MglMap ref="mapRef" :map-style="osmStyle" height="340px" width="100%">
    <MglNavigationControl />
    <mgl-marker
      v-for="marker in markers.filter((m) => m.lat && m.long)"
      :key="marker.id"
      :coordinates="getCoordinates(marker) || { lng: 0, lat: 0 }"
      :color="marker.color || defaultColor"
    >
      <mgl-popup v-if="marker.name">
        <nuxt-link :to="marker.to">
          <h3>{{ marker.name }}</h3>
        </nuxt-link>
      </mgl-popup>
    </mgl-marker>
  </MglMap>
</template>
