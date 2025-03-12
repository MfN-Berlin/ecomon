import { defineNuxtPlugin } from "#app";

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();

  const logger = createLogger({
    logLevel: config.public.LOG_LEVEL || "info",
    logFormat: config.LOG_FORMAT || "simple"
  });

  return {
    provide: {
      logger
    }
  };
});
