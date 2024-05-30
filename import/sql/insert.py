def insert_record(
    prefix, filepath, filename, record_datetime, duration, channels, corrupted
):
    return """INSERT INTO {}_records (filepath, filename, record_datetime, duration, channels, corrupted)
VALUES ( '{}', '{}', '{}', {}, {}, {});""".format(
        prefix, filepath, filename, record_datetime, duration, channels, corrupted
    )


def insert_prediction(prefix, record_id, start_time, end_time, channel, predictions, species):
    prediction_list = ",".join([str(x) for x in predictions])
    species_list = ",".join([str(x) for x in species])
    return f"""INSERT INTO {prefix}_predictions ( record_id, start_time, end_time, channel, {species_list}) 
    VALUES ({record_id}, {start_time}, {end_time}, '{channel}', {prediction_list})"""
