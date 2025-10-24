# Ecomon DB indices

## Dashboard

### Critical
```
CREATE INDEX IF NOT EXISTS idx_records_site_datetime ON records(site_id, record_datetime);
CREATE INDEX IF NOT EXISTS idx_mir_compound ON model_inference_results(model_id, label_id, confidence, record_id);
```

### Secondary
```
CREATE INDEX IF NOT EXISTS idx_mir_record_id ON model_inference_results(record_id);
```

### Redundant
```
DROP INDEX IF EXISTS idx_mir_model_label_confidence;
```

## Data tables / Records

### Keep

```
-- "idx_inference_results_record_confidence" - record-based queries
-- "idx_inference_results_record_covering" - covering index for record queries
-- "idx_model_inference_results_performance" - model-based performance queries
```
### Add
```
CREATE INDEX IF NOT EXISTS idx_mir_general_purpose
ON model_inference_results(model_id, label_id, start_time, confidence)
INCLUDE (record_id);

CREATE INDEX IF NOT EXISTS idx_mir_time_series
ON model_inference_results(start_time, model_id, label_id, confidence, record_id);

CREATE INDEX CONCURRENTLY idx_records_pagination
ON records(id DESC);

CREATE INDEX CONCURRENTLY idx_records_datetime_filepath
ON records(record_datetime DESC, filepath text_pattern_ops, id DESC)
INCLUDE (site_id, filename, duration, channels, mime_type, sample_rate, created_at);

CREATE INDEX CONCURRENTLY idx_records_datetime_ordered
ON records(record_datetime DESC, id DESC)
WHERE record_datetime IS NOT NULL;

```



### Redundant
```
DROP INDEX IF EXISTS idx_model_inference_results_label_id;
DROP INDEX IF EXISTS idx_model_record;
```
