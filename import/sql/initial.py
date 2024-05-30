def check_record_table_exists(prefix):
    return """
    SELECT count(id) FROM {}_records
    """.format(
        prefix
    )


def check_record_predictions_exists(prefix):
    return """
    SELECT count(id) FROM {}_predictions
    """.format(
        prefix
    )

def create_record_table(prefix):
    return f"""
    CREATE TABLE IF NOT EXISTS {prefix}_records (
      id SERIAL PRIMARY KEY,
      filepath VARCHAR(320) NOT NULL,
      filename VARCHAR(128) NOT NULL,
      record_datetime TIMESTAMP NULL,
      duration DECIMAL(11, 6) NOT NULL,
      channels SMALLINT NOT NULL,
      corrupted SMALLINT NOT NULL,
      UNIQUE (filepath)
    );
    CREATE INDEX {prefix}_record_datetime_index ON {prefix}_records (record_datetime);
    """


def create_predictions_table(prefix, species):
    rows = " ".join(['"{}" FLOAT NOT NULL,\n'.format(s) for s in species])

    return f"""
    CREATE TABLE IF NOT EXISTS {prefix}_predictions (
      id BIGSERIAL PRIMARY KEY,
      record_id INT NOT NULL,
      start_time DECIMAL(11, 6) NULL,
      end_time DECIMAL(11, 6) NULL,
      channel VARCHAR(8) NOT NULL,
      {rows}
      FOREIGN KEY (record_id) REFERENCES {prefix}_records (id) ON DELETE CASCADE
    );
    CREATE INDEX {prefix}_channel_index ON {prefix}_predictions (channel);
    """