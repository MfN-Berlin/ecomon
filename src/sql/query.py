import random


def get_record_id_by_filepath(prefix, filepath):
    return """
    SELECT id from {}_records where filepath = '{}'
    """.format(
        prefix, filepath
    )


def get_prediction_random_sample(
    prefix, sample_size, species, threshold, random_seed=None
):
    if random_seed is None:
        random_seed = random.randint(0, 2147483647)
    return """
    SELECT
    filepath,
    record_datetime,
    start_time,
    end_time,
    channel,
    {species}
    FROM {prefix}_predictions
    JOIN {prefix}_records ON {prefix}_predictions.record_id = {prefix}_records.id
    WHERE {species} >= '{threshold}'
    ORDER by rand({random_seed})
    limit {sample_size}
    """.format(
        prefix=prefix,
        sample_size=sample_size,
        species=species,
        threshold=threshold,
        random_seed=random_seed,
    )

