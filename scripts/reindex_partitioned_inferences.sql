DO $$
DECLARE
    partition_name text;
    i int;
BEGIN
    RAISE NOTICE 'Starting index creation for 200 partitions...';

    FOR i IN 1..200 LOOP
        partition_name := 'mir_partitions.model_inference_results_p' || lpad(i::text, 3, '0');

        RAISE NOTICE 'Processing partition % (p%)', i, lpad(i::text, 3, '0');

        -- Create confidence index
        EXECUTE 'CREATE INDEX IF NOT EXISTS model_inference_results_p' || lpad(i::text, 3, '0') || '_confidence_idx ON ' || partition_name || ' USING btree (confidence)';
        RAISE NOTICE '  Created confidence index for p%', lpad(i::text, 3, '0');

        -- Create label_id index
        EXECUTE 'CREATE INDEX IF NOT EXISTS model_inference_results_p' || lpad(i::text, 3, '0') || '_label_id_idx ON ' || partition_name || ' USING btree (label_id)';
        RAISE NOTICE '  Created label_id index for p%', lpad(i::text, 3, '0');

        -- Create model_id index
        EXECUTE 'CREATE INDEX IF NOT EXISTS model_inference_results_p' || lpad(i::text, 3, '0') || '_model_id_idx ON ' || partition_name || ' USING btree (model_id)';
        RAISE NOTICE '  Created model_id index for p%', lpad(i::text, 3, '0');

        -- Create start_time_end_time index
        EXECUTE 'CREATE INDEX IF NOT EXISTS model_inference_results_p' || lpad(i::text, 3, '0') || '_start_time_end_time_idx ON ' || partition_name || ' USING btree (start_time, end_time)';
        RAISE NOTICE '  Created start_time_end_time index for p%', lpad(i::text, 3, '0');

        -- Progress update every 10 partitions
        IF i % 10 = 0 THEN
            RAISE NOTICE 'Completed %/200 partitions (%.1f%%)', i, (i::float/200)*100;
        END IF;
    END LOOP;

    RAISE NOTICE 'All indexes created successfully for 200 partitions!';
END $$;