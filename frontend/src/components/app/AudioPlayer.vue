<script setup lang="ts">
import { useAVBars } from "vue-audio-visual";

const store = useAudioPlayerStore();
const player = ref<HTMLAudioElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);
const { playing, currentTime, duration, seeking, waiting } = useMediaControls(player);

let avBarsInstance = null;

function resetAudioPlayerElement() {
  if (player.value) {
    player.value.pause();
    player.value.currentTime = 0;
    player.value.src = "";
    player.value.load();
  }
}

function cleanupAVBars() {
  if (avBarsInstance) {
    try {
      // Check if useAVBars provides a cleanup method
      if (typeof avBarsInstance.destroy === 'function') {
        avBarsInstance.destroy();
      } else if (avBarsInstance.audioContext) {
        avBarsInstance.audioContext.close();
      }
    } catch (error) {
      console.warn("Error cleaning up AVBars:", error);
    }
    avBarsInstance = null;
  }

  if (store.audioContext) {
    try {
      store.audioContext.close();
    } catch (error) {
      console.warn("Error closing store audio context:", error);
    }
    store.audioContext = null;
  }
}

watch(playing, (value) => {
  store.playing = value;
});

watch(waiting, (value) => {
  store.seeking = value || seeking.value;
});

watch(
  () => store.visible,
  (value) => {
    if (value) {
      // Always cleanup first
      cleanupAVBars();
      resetAudioPlayerElement();

      // Small delay to ensure cleanup is complete
      nextTick(() => {
        try {
          avBarsInstance = useAVBars(player, canvas, {
            barColor: "lime"
          });

          if (avBarsInstance && avBarsInstance.audioContext) {
            store.audioContext = avBarsInstance.audioContext;
          }
        } catch (error) {
          console.error("Error creating AVBars:", error);
          avBarsInstance = null;
        }
      });
    } else {
      cleanupAVBars();
      resetAudioPlayerElement();
    }
  }
);

// Clean up on component unmount
onUnmounted(() => {
  cleanupAVBars();
  resetAudioPlayerElement();
});
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