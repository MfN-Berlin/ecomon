import { defineStore } from "pinia";

type UiState = {
  drawerVisible: boolean;

  darkMode: boolean;
};
export const useUiStore = defineStore("ui", {
  state: (): UiState => ({
    drawerVisible: true,
    darkMode: false
  }),
  actions: {
    setDrawerVisibility(visible: boolean) {
      this.drawerVisible = visible;
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    }
  }
});
