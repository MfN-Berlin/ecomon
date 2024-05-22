import json
import random
from pymysql.converters import escape_string
from routes.route_types import JobStatus, JobTypes
from os import getenv


def get_prediction_file_distinct_max_sample(prefix, species, sample_size=10):
    return f"""
    SELECT
    r.filepath,
    r.record_datetime,
    r.filename,
    p.start_time,
    p.end_time,
    r.duration,
    p.channel,
    p.max_confidence as {species}
FROM
    (SELECT
        record_id,
        start_time,
        end_time,
        channel,
        {species} AS max_confidence,
        ROW_NUMBER() OVER(PARTITION BY record_id ORDER BY {species} DESC) AS rn
    FROM {prefix}_predictions
    ) AS p
JOIN {prefix}_records AS r ON p.record_id = r.id
WHERE p.rn = 1
ORDER BY p.max_confidence DESC
LIMIT {sample_size};
    """


def get_prediction_max_sample(
    prefix,
    species,
    sample_size=10,
    audio_padding=0,
):
    enlarged_sample_size = sample_size * 3
    return f"""
SELECT
    r.filepath,
    r.record_datetime,
    r.filename,
    p.start_time,
    p.end_time,
    r.duration,
    p.channel,
    p.{species}
FROM (
    SELECT * FROM {prefix}_predictions
    WHERE
        start_time >= {audio_padding}
        ORDER BY {species} DESC
        LIMIT {enlarged_sample_size}
    ) AS p
JOIN {prefix}_records AS r ON p.record_id = r.id
WHERE
    p.end_time + {audio_padding} <= r.duration
LIMIT {sample_size};
    """


def get_prediction_random_sample(
    prefix,
    sample_size,
    species,
    threshold_min,
    threshold_max,
    random_seed=None,
    audio_padding=None,
    start_datetime=None,
    end_datetime=None,
):
    if random_seed is None:
        random_seed = random.randint(0, 2147483647)
    return """
    SELECT
    filepath,
    record_datetime,
    start_time,
    end_time,
    duration,
    channel,
    {species},
    filename
    FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE
    {start_datetime}
    {end_datetime}
    {threshold_min}
    {threshold_max}
    {padding}
    ORDER by rand({random_seed})
    limit {sample_size}
    """.format(
        prefix=prefix,
        species=species,
        padding=" start_time >= {audio_padding} AND end_time + {audio_padding} <= duration".format(
            audio_padding=audio_padding
        )
        if audio_padding != None
        else "",
        start_datetime="record_datetime >= '{}' AND".format(start_datetime)
        if start_datetime != None
        else "",
        end_datetime="record_datetime <= '{}' AND".format(end_datetime)
        if end_datetime != None
        else "",
        threshold_min="  {} >= '{}' AND".format(species, threshold_min)
        if threshold_min != None or threshold_min == 0
        else "",
        threshold_max="  {} <= '{}' AND".format(species, threshold_max)
        if threshold_max != None or threshold_min == 1
        else "",
        random_seed=random_seed,
        sample_size=sample_size,
    )


def get_predictions_with_file_id(
    prefix,
    species,
    threshold_min,
    threshold_max,
    audio_padding=None,
    start_datetime=None,
    end_datetime=None,
):
    return """
    SELECT
    record_id,
    filepath,
    record_datetime,
    start_time,
    end_time,
    duration,
    channel,
    {species},
    filename
    FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE
    {start_datetime}
    {end_datetime}
    {threshold_min}
    {threshold_max}
    {padding}
    """.format(
        prefix=prefix,
        species=species,
        padding=" start_time >= {audio_padding} AND end_time + {audio_padding} <= duration".format(
            audio_padding=audio_padding
        )
        if audio_padding != None
        else "",
        start_datetime="record_datetime >= '{}' AND".format(start_datetime)
        if start_datetime != None
        else "",
        end_datetime="record_datetime <= '{}' AND".format(end_datetime)
        if end_datetime != None
        else "",
        threshold_min=" {} >= '{}' AND".format(species, threshold_min)
        if threshold_min != None or threshold_min == 0
        else "",
        threshold_max=" {} <= '{}' AND".format(species, threshold_max)
        if threshold_max != None or threshold_min == 1
        else "",
    )


def get_predictions(
    prefix,
    species,
    threshold_min,
    threshold_max,
    audio_padding=None,
    start_datetime=None,
    end_datetime=None,
):
    return """
    SELECT
    filepath,
    record_datetime,
    start_time,
    end_time,
    duration,
    channel,
    {species},
    filename
    FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE
    {start_datetime}
    {end_datetime}
    {threshold_min}
    {threshold_max}
    {padding}
    """.format(
        prefix=prefix,
        species=species,
        padding="start_time >= {audio_padding} AND end_time + {audio_padding} <= duration".format(
            audio_padding=audio_padding
        )
        if audio_padding != None
        else "",
        start_datetime="record_datetime >= '{}' AND".format(start_datetime)
        if start_datetime != None
        else "",
        end_datetime="record_datetime <= '{}' AND".format(end_datetime)
        if end_datetime != None
        else "",
        threshold_min=" {} >= '{}' AND".format(species, threshold_min)
        if threshold_min != None or threshold_min == 0
        else "",
        threshold_max=" {} <= '{}' AND".format(species, threshold_max)
        if threshold_max != None or threshold_min == 1
        else "",
    )


def get_datetime_of_first_record_in_sql_table(table_name: str):
    return """
    SELECT * FROM {} ORDER BY record_datetime ASC LIMIT 1
    """.format(
        table_name
    )


def get_datetime_of_last_record_in_sql_table(table_name: str):
    return """
    SELECT * FROM {} ORDER BY record_datetime DESC LIMIT 1
    """.format(
        table_name
    )


def get_column_names_of_sql_table_query(table_name: str):
    return """
    SELECT column_name FROM information_schema.columns WHERE table_name = '{}'
    """.format(
        table_name
    )


def create_index_for_sql_table(table_name: str, column_name: str):
    return """
    CREATE INDEX {}_index ON {}({})
    """.format(
        column_name, table_name, column_name
    )


# drop index for column with index_name and table_name
def drop_index_for_sql_table(table_name, column_name):
    return """
    ALTER TABLE {} DROP INDEX {}_index
    """.format(
        table_name, column_name
    )


def count_entries_in_sql_table(table_name: str):
    return """
    SELECT count(*) FROM {}
    """.format(
        table_name
    )


def count_predictions(prefix):
    return """
    SELECT count(*) FROM {prefix}_predictions
    """.format(
        prefix=prefix
    )


def get_index_names_of_sql_table_ending_with(table_name: str, ending: str):
    return """
    SELECT index_name FROM information_schema.statistics WHERE table_name = '{}' AND index_name like '%{}'
    """.format(
        table_name, ending
    )


def sum_values_of_sql_table_column(table_name: str, column_name: str):
    return """
    SELECT sum({}) FROM {}
    """.format(
        column_name, table_name
    )


def count_predictions_in_date_range(prefix, start_datetime, end_datetime):
    return """
    SELECT count(*) FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE record_datetime >= '{start_datetime}' AND record_datetime <= '{end_datetime}' AND start_time >= 5 AND end_time + 5 <= duration
    """.format(
        start_datetime=start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        end_datetime=end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        prefix=prefix,
    )


def get_predictions_in_date_range(
    prefix,
    species,
    start_datetime,
    end_datetime,
    min_threshold=None,
    max_threshold=None,
):
    return """
    SELECT record_datetime, start_time, {species} FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE record_datetime >= '{start_datetime}' AND record_datetime <= '{end_datetime}' AND start_time >= 5 AND end_time + 5 <= duration
    {min_threshold}
    {max_threshold}
    ORDER BY record_datetime ASC
    """.format(
        species=species,
        start_datetime=start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        end_datetime=end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        prefix=prefix,
        min_threshold=" AND {} >= {}".format(species, min_threshold)
        if min_threshold != None
        else "",
        max_threshold=" AND {} <= {}".format(species, max_threshold)
        if max_threshold != None
        else "",
    )


def count_species_over_threshold_in_date_range(
    prefix, species, threshold_min, threshold_max, start_datetime, end_datetime
):
    return """
    SELECT count(*) FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id

    WHERE record_datetime >= '{start_datetime}' AND record_datetime <= '{end_datetime}' {threshold_min} {threshold_max} AND start_time >= 5 AND end_time + 5 <= duration
    """.format(
        start_datetime=start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        end_datetime=end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        species=species,
        threshold_min="AND {} >= '{}'".format(species, threshold_min)
        if threshold_min != None or threshold_min == 0
        else "",
        threshold_max="AND {} <= '{}'".format(species, threshold_max)
        if threshold_max != None or threshold_min == 1
        else "",
        prefix=prefix,
    )


def get_all_prediction_table_names():
    return f"""
    SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = '{getenv('MDAS_MARIADB_DATABASE')}' and TABLE_NAME like '%_predictions'
    """


def get_all_jobs(prefix=None, type=None, status=None) -> str:
    filters = [
        f
        for f in [("prefix", prefix), ("type", type), ("status", status)]
        if f[1] is not None
    ]
    if len(filters) == 0:
        return """
        SELECT * FROM jobs ORDER BY created_at DESC
        """
    else:
        return """
        SELECT * FROM jobs WHERE {} ORDER BY created_at DESC
        """.format(
            " AND ".join(
                ["{} = '{}'".format(c_name, value) for c_name, value in filters]
            )
        )


def get_job_by_id(job_id):
    return """
    SELECT * FROM jobs WHERE id = {}
    """.format(
        job_id
    )


def add_job(prefix: str, type: JobTypes, status: JobStatus, metadata: dict):
    metadata_str = escape_string(json.dumps(metadata))
    print(f"prefix: {prefix}")
    print(f"type: {type}")
    print(f"status: {status}")
    print(f"metadata: {metadata_str}")
    query = f"INSERT INTO jobs (prefix, type, status,metadata) VALUES ('{prefix}', '{type}', '{status}', '{metadata_str}')"
    print(f"query: {query}")
    return query


def update_job_metadata(job_id: int, metadata: dict):
    metadata_str = escape_string(json.dumps(metadata))
    return """
    UPDATE jobs SET metadata = '{}' WHERE id = {}
    """.format(
        metadata_str, job_id
    )


def update_job_status(job_id: int, status: JobStatus):
    return """
    UPDATE jobs SET status = '{}' WHERE id = {}
    """.format(
        status, job_id
    )


def update_job_progress(job_id: int, progress: int):
    return """
    UPDATE jobs SET progress = '{}' WHERE id = {}
    """.format(
        progress, job_id
    )


def update_job_failed(job_id: int, error):
    escaped = escape_string(error)
    return """
    UPDATE jobs SET status = 'failed', error = '{}' WHERE id = {}
    """.format(
        escaped, job_id
    )


def delete_job(job_id: int):
    return """
    DELETE FROM jobs WHERE id = {}
    """.format(
        job_id
    )


def get_max_updated_at_from_jobs():
    return """
    SELECT max(updated_at) FROM jobs
    """
