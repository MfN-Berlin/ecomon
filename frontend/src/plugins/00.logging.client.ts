import { defineNuxtPlugin } from "#app";
import { createConsola } from "consola";

function mapLogLevel(logLevel: string) {
  switch (logLevel.toLowerCase()) {
    case "error":
      return 0;
    case "warn":
      return 1;
    case "info":
      return 3;
    case "debug":
      return 4;
    case "trace":
      return 5;
    default:
      return 3;
  }
}

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();

  const logger = createConsola({
    level: mapLogLevel(config.public.LOG_LEVEL || "info")
  });

  return {
    provide: {
      logger
    }
  };
});
