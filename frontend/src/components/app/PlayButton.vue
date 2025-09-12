<script setup lang="ts">
import { debounce } from 'lodash-es';
import { files } from "eslint-plugin-prettier/recommended";

const props = defineProps<{
  src: string;
}>();
const isPlaying = computed(() => audioPlayerStore.playing && audioPlayerStore.getSrc() === props.src);
const isLoading = computed(() => audioPlayerStore.seeking && audioPlayerStore.getSrc() === props.src);
const audioPlayerStore = useAudioPlayerStore();

const debouncedPlay = debounce(() => {
  if (isPlaying.value) {
    audioPlayerStore.close();
  } else {
    const test = "http://localhost:3000/ecomon_next/audio/test.flac";
    audioPlayerStore.play(test);
    // audioPlayerStore.play(props.src);
  }
}, 300); // 300ms debounce


function play() {
  debouncedPlay();
}
</script>

<template>
  <v-btn
    v-bind="$attrs"
    :icon="isPlaying ? 'mdi-pause' : 'mdi-play'"
    :loading="isLoading"
    color="primary"
    @click="play"
  >
  </v-btn>
</template>
