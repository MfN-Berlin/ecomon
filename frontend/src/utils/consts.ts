export const enum QUERY_KEYS {
  locations = "location",
  models = "model",
  sites = "site",
  dataDirectories = "dataDirectories",
  records = "record",
  jobs = "job",
  siteJobs = "siteJobs",
  sets = "set",
  labels = "label",
  siteReports = "siteReport",
  siteReportsList = "siteReportsList",
  siteReportsMonthlyHistogram = "siteReportsMonthlyHistogram",
  siteReportsDailyHistogram = "siteReportsDailyHistogram",
  siteReportsDurationHistogram = "siteReportsDurationHistogram",
  siteReportsRecordsHeatmap = "siteReportsRecordsHeatmap",
  siteFirstLastRecordDate = "siteFirstLastRecordDate",
  recordModelInferenceResults = "recordModelInferenceResults"
}

export const enum RECORD_ERRORS {
  FILE_READ_ERROR = "file_read_error",
  MISSING_FILE_PREFIX = "missing_file_prefix",
  RECORD_DATETIME_FORMAT = "record_datetime_format",
  DURATION_MISSMATCH = "duration_missmatch",
  SAMPLERATE_MISSMATCH = "samplerate_missmatch"
}
