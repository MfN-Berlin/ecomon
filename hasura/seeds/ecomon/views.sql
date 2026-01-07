CREATE OR REPLACE VIEW model_inference_results_view AS
SELECT
    id,
    model_id,
    record_id,
    label_id,
    start_time,
    end_time,
    confidence
FROM model_inference_results_pt_record;