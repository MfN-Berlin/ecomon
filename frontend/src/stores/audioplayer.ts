import { defineStore } from "pinia";

type AudioPlayerState = {
  src: string | undefined;
  visible: boolean;
};
export const useAudioPlayerStore = defineStore("audioplayer", {
  state: (): AudioPlayerState => ({
    src: undefined,
    visible: false
  }),
  actions: {
    play(src: string) {
      this.src = src;
      this.visible = true;
    },
    close() {
      this.src = undefined;
      this.visible = false;
    }
  }
});
