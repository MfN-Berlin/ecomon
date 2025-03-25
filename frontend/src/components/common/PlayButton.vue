<script setup lang="ts">
import { files } from "eslint-plugin-prettier/recommended";

const props = defineProps<{
  src: string;
}>();
const isPlaying = computed(() => audioPlayerStore.playing && audioPlayerStore.getSrc() === props.src);
const audioPlayerStore = useAudioPlayerStore();

function play() {
  if (isPlaying.value) {
    audioPlayerStore.close();
  } else {
    audioPlayerStore.play(props.src);
  }
}
</script>

<template>
  <v-btn :icon="isPlaying ? 'mdi-pause' : 'mdi-play'" v-bind="$attrs" color="primary" @click="play"> </v-btn>
</template>
