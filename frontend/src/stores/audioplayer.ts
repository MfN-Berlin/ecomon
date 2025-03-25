import { defineStore } from "pinia";

type AudioPlayerState = {
  src: string | undefined;
  visible: boolean;
  playing: boolean;
};
export const useAudioPlayerStore = defineStore("audioplayer", {
  state: (): AudioPlayerState => ({
    src: undefined,
    visible: false,
    playing: false
  }),
  actions: {
    play(src: string) {
      this.src = src + "#" + Date.now();
      this.visible = true;
    },
    close() {
      this.src = undefined;
      this.visible = false;
    },
    getSrc() {
      return this.src?.split("#")[0];
    }
  }
});
