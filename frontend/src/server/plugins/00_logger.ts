import { createLogger } from "~/utils/server-logger";

export default defineNitroPlugin((nitroApp) => {
  const config = useRuntimeConfig();
  const logLevel = config.public.LOG_LEVEL;
  const logger = createLogger({
    logLevel,
    logFormat: config.LOG_FORMAT || "simple"
  });

  nitroApp.hooks.hook("error", async (error, { event }) => {
    const headers = event ? getRequestHeaders(event) : undefined;
    const query = event ? getQuery(event) : undefined;
    logger.error(`application error`, {
      method: event?.method,
      path: event?.path,
      headers: headers,
      query,
      ...error
    });
  });

  nitroApp.hooks.hook("request", (event) => {
    const headers = logLevel === "debug" ? getRequestHeaders(event) : undefined;
    const query = getQuery(event);
    logger.info("request", {
      method: event.method,
      path: event.path,
      headers: headers,
      query
    });
  });

  //   nitroApp.hooks.hook("beforeResponse", (event, { body }) => {

  //  });

  //   nitroApp.hooks.hook("afterResponse", (event, { body }) => {

  //   });
});
