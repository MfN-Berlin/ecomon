def insert_record(prefix, filepath, filename, record_datetime, duration, channels):
    return """INSERT INTO ${prefix}_records (filepath, filename,record_datetime,   duration, channels)
VALUES ('${}', '${}', '${}', ${},${});""".format(
        prefix, filepath, filename, record_datetime, duration, channels
    )


def insert_prediction(prefix, record_id, start_time, end_time, channel, predictions):

    return """
    INSERT INTO ${}_predictions 
VALUES (record_id, start_time,end_time, channel, predictions); SELECT * FROM bai.test_records;
    """.format(
        prefix,
        filepath,
        filename,
        record_datetime,
        duration,
        channels,
        predictions_string,
    )
