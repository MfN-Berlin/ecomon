#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create jobs table
    CREATE TABLE IF NOT EXISTS jobs (
      id SERIAL PRIMARY KEY,
      prefix VARCHAR(256) NOT NULL,
      status VARCHAR(10) NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'done', 'failed', 'pending')),
      type VARCHAR(32) CHECK (type IN ('add_index', 'drop_index', 'create_sample', 'calc_bin_sizes', 'calc_predictions', 'calc_daily_histograms', 'calc_activation', 'create_voucher')),
      metadata JSON,
      progress INT NOT NULL DEFAULT 0,
      error VARCHAR(256),
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE UNIQUE INDEX IF NOT EXISTS id_UNIQUE ON jobs (id);
    CREATE INDEX IF NOT EXISTS prefix_index ON jobs (prefix);
    CREATE INDEX IF NOT EXISTS updated_at_index ON jobs (updated_at);
    CREATE INDEX IF NOT EXISTS created_at_index ON jobs (created_at);

    -- Create collections table
    CREATE TABLE IF NOT EXISTS collections (
      id SERIAL PRIMARY KEY,
      prefix VARCHAR(64) NOT NULL,
      first_record TIMESTAMP,
      last_record TIMESTAMP,
      record_count INT NOT NULL DEFAULT 0,
      record_duration INT NOT NULL DEFAULT 0,
      prediction_count INT NOT NULL DEFAULT 0,
      corrupted_record_count INT NOT NULL DEFAULT 0,
      model_name VARCHAR(64) NOT NULL,
      inference_window_size INT NOT NULL DEFAULT 0,
      record_regime_recording_duration INT NOT NULL DEFAULT 0,
      record_regime_pause_duration INT NOT NULL DEFAULT 0,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE (id)
    );

    CREATE UNIQUE INDEX IF NOT EXISTS id_UNIQUE ON collections (id);
    CREATE INDEX IF NOT EXISTS prefix_index ON collections (prefix);
    CREATE INDEX IF NOT EXISTS updated_at_index ON collections (updated_at);
    CREATE INDEX IF NOT EXISTS created_at_index ON collections (created_at);

    -- Create or replace function to update updated_at column
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS \$\$
    BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
    END;
    \$\$ LANGUAGE 'plpgsql';

    -- Create triggers for both tables
    CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE
    ON jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_collections_updated_at BEFORE UPDATE
    ON collections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EOSQL
