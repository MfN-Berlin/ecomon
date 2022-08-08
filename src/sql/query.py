import random


def get_record_id_by_filepath(prefix, filepath):
    return """
    SELECT id from {}_records where filepath = '{}'
    """.format(
        prefix, filepath
    )


def get_prediction_random_sample(
    prefix,
    sample_size,
    species,
    threshold,
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
    {species}
    FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE
    {start_datetime}
    {end_datetime}
    {species} >= '{threshold}'
    {padding}
    ORDER by rand({random_seed})
    limit {sample_size}
    """.format(
        prefix=prefix,
        sample_size=sample_size,
        species=species,
        padding="AND start_time >= {audio_padding} AND end_time + {audio_padding} <= duration".format(
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
        threshold=threshold,
        random_seed=random_seed,
    )

