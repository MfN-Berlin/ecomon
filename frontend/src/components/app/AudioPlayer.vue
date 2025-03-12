<script setup lang="ts">
import { useAVBars } from "vue-audio-visual";

const store = useAudioPlayerStore();
const player = ref<HTMLAudioElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);
const container = ref<HTMLElement | null>;

useAVBars(player, canvas, {
  barColor: "lime"
});
</script>

<template>
  <v-sheet v-if="store.visible" color="surface" height="200" class="position-relative">
    <div ref="container" class="d-flex flex-column position-absolute top-0 left-0 w-100 h-100">
      <canvas ref="canvas" class="w-100" style="height: 120px" />
      <audio ref="player" :src="store.src" controls autoplay class="w-100 mt-4" />
    </div>
    <div class="position-absolute top-0 right-0 pa-2">
      <v-btn density="comfortable" icon="$close" variant="plain" @click="store.close"></v-btn>
    </div>
  </v-sheet>
</template>
