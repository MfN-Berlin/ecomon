import type { Logform } from "winston";
import { format, createLogger as winstonCreateLogger, transports, config as winstonConfig } from "winston";

export function createLogger({
  logLevel,
  logFormat
}: {
  logLevel: string | undefined;
  logFormat: string | undefined;
}) {
  const appFormat = format((info) => {
    const { app, ...rest } = info;
    return app ? { ...rest, message: `[${app}] ${rest.message}` } : info;
  });

  const logFormats: {
    readonly json: Logform.Format;
    readonly simple: Logform.Format;
  } = {
    json: format.json(),
    simple: format.combine(format.colorize(), appFormat(), format.simple())
  } as const;

  const logger = winstonCreateLogger({
    level: logLevel || "info",
    format: logFormats[logFormat === "json" ? "json" : "simple"],
    levels: winstonConfig.syslog.levels,
    transports: [
      new transports.Console({
        stderrLevels: ["error", "warn", "info", "debug"]
      })
    ]
  });

  return logger;
}
