import { defineStore } from "pinia";

type UiState = {
  drawerVisible: boolean;
};
export const useUiStore = defineStore("ui", {
  state: (): UiState => ({
    drawerVisible: true
  }),
  actions: {
    setDrawerVisibility(visible: boolean) {
      this.drawerVisible = visible;
    }
  }
});
