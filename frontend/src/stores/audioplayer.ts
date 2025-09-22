import { defineStore } from "pinia";

type AudioPlayerState = {
  src: string | undefined;
  visible: boolean;
  playing: boolean;
  seeking: boolean;
  audioContext: AudioContext | null;
};
export const useAudioPlayerStore = defineStore("audioplayer", {
  state: (): AudioPlayerState => ({
    src: undefined,
    visible: false,
    playing: false,
    seeking: false,
    audioContext: null,
  }),
  actions: {
    resetAudioPlayer() {
      // This will be called to clean up audio contexts
      if (this.audioContext) {
        try {
          this.audioContext.close();
        } catch (error) {
          console.warn("Error closing audio context:", error);
        }
        this.audioContext = null;
      }
    },
    play(src: string) {
      this.close();

      // Small delay to ensure cleanup is complete
      setTimeout(() => {
        this.src = src + "#" + Date.now();
        this.visible = true;
      }, 50);
    },
    close() {
      this.resetAudioPlayer();
      this.src = undefined;
      this.visible = false;
      this.playing = false;
      this.seeking = false;
    },
    getSrc() {
      return this.src?.split("#")[0];
    }
  }
});
