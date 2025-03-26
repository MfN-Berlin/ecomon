<script setup lang="ts">
import { useAVBars } from "vue-audio-visual";

const store = useAudioPlayerStore();
const player = ref<HTMLAudioElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);
const { playing, currentTime, duration, seeking, waiting } = useMediaControls(player);
watch(playing, (value) => {
  console.log("Audioplayer", value);
  store.playing = value;
});
watch(
  () => store.visible,
  (value) => {
    if (value) {
      useAVBars(player, canvas, {
        barColor: "lime"
      });
    } else {
      player.value?.pause();
    }
  }
);
watch(waiting, (value) => {
  store.seeking = value || seeking.value;
});

// <v-sheet v-if="store.visible" color="surface" v-bind="$attrs">
//   <div ref="container" class="d-flex flex-column position-absolute top-0 left-0 w-100 h-100">
//
//     <audio ref="player" :src="store.src" controls autoplay class="w-100 mt-4" />
//   </div>
//   <div class="position-absolute top-0 right-0 pa-2">
//     <v-btn density="comfortable" icon="$close" variant="plain" @click="store.close"></v-btn>
//   </div>
// </v-sheet>
</script>

<template>
  <v-card v-if="store.visible" color="surface" v-bind="$attrs">
    <v-card-title class="d-flex justify-space-between align-center pa-0">
      <audio ref="player" :src="store.src" controls autoplay class="w-100 mt-4" />

      <v-btn icon="mdi-close" variant="text" @click="store.close"></v-btn>
    </v-card-title>

    <v-card-text>
      <canvas ref="canvas" class="w-100" style="height: 120px" />
    </v-card-text>
  </v-card>
</template>
