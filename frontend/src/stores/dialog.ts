import { defineStore } from "pinia";

type DialogOptions = {
  okLabel?: string;
  cancelLabel?: string;
  persistent?: boolean;
  width?: string;
};

export type DialogState = {
  title: string;
  message: string;
  callbackFn: () => Promise<void> | void;
  visible: boolean;
  options: DialogOptions;
};
const defaultOptions: DialogOptions = {
  okLabel: "OK",
  cancelLabel: "Cancel",
  persistent: false,
  width: "400px"
};

export const useDialogStore = defineStore("dialog", {
  state: (): DialogState => ({
    title: "",
    message: "",
    callbackFn: () => {},
    visible: false,
    options: defaultOptions
  }),

  actions: {
    openDialog(
      title: string,
      message: string,
      callbackFn: () => void,
      options: DialogOptions = defaultOptions
    ) {
      this.title = title;
      this.message = message;
      this.callbackFn = callbackFn;
      this.visible = true;
      this.options = { ...defaultOptions, ...options };
    }
  }
});
