import { defineNuxtPlugin } from "#app";

export default defineNuxtPlugin(() => {
  const currentTime = ref(new Date());
  const currentTimeString = computed(() => {
    return currentTime.value.toISOString();
  });

  setInterval(() => {
    currentTime.value = new Date();
  }, 1000);

  return {
    provide: {
      currentTime,
      currentTimeString
    }
  };
});
